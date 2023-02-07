
# python3 eval_IW.py --network /home/ericlab/gr_convnet/robotic-grasping/logs/IW_jacqurd/gradation2/epoch_91_iou_0.92 --dataset jacquard --dataset-path /home/ericlab/jacquard_dataset --iou-eval 
# python3 eval_OW.py --network /home/ericlab/gr_convnet/robotic-grasping/logs/OW_jacqurd/drop/epoch_90_iou_0.93 --dataset jacquard --dataset-path /home/ericlab/jacquard_dataset --iou-eval 
# python3 eval_IW.py --network /home/ericlab/gr_convnet/robotic-grasping/logs/IW_jacqurd/graduation2-2/epoch_99_iou_0.92 --dataset jacquard --dataset-path /home/ericlab/jacquard_dataset --iou-eval 
import torch.nn as nn
import torch.nn.functional as F
import torch
from inference.models.grasp_model import GraspModel, SE_identity,SCSEBlock,ResidualBlock


class GenerativeResnet(GraspModel):

    def __init__(self, input_channels=1, dropout=False, prob=0.0, channel_size=32):
        super(GenerativeResnet, self).__init__()
        self.conv1 = nn.Conv2d(input_channels, channel_size, kernel_size=9, stride=1, padding=4)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.res1 = SE_identity(128, 128)
        self.res2 = SE_identity(128, 128)
        self.res3 = SE_identity(128, 128)
        self.res4 = SE_identity(128, 128)
        self.res5 = SE_identity(128, 128)
        # self.res4 = ResidualBlock(128, 128)
        # self.res5 = ResidualBlock(128, 128)
        
        self.conv4 = nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1, output_padding=1)
        self.bn4 = nn.BatchNorm2d(64)

        self.res6 = ResidualBlock(64, 64)
        self.attention1 = SCSEBlock(64,64)
        
        self.conv5 = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=2, output_padding=1)
        self.bn5 = nn.BatchNorm2d(32)

        self.res7 = ResidualBlock(32, 32)
        self.attention2 = SCSEBlock(32,32)

        self.conv6 = nn.ConvTranspose2d(32, 32, kernel_size=9, stride=1, padding=4)
        self.bn6 = nn.BatchNorm2d(32)


        self.pos_output = nn.Conv2d(32, 1, kernel_size=2)
        self.cos_output = nn.Conv2d(32, 1, kernel_size=2)
        self.sin_output = nn.Conv2d(32, 1, kernel_size=2)
        self.width_output = nn.Conv2d(32, 1, kernel_size=2)
        
        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.xavier_uniform_(m.weight, gain=1)

    def forward(self, x_in):
        x = F.relu(self.bn1(self.conv1(x_in)))

        x = F.relu(self.bn2(self.conv2(x)))

        x = F.relu(self.bn3(self.conv3(x)))

        x = self.res1(x)
        x = self.res2(x)
        x = self.res3(x)
        x = self.res4(x)
        x = self.res5(x)

        x = F.relu(self.bn4(self.conv4(x)))
        x1 = self.attention1(x)
        x2 = self.res6(x)
        x = x1+x2
        
        x = F.relu(self.bn5(self.conv5(x)))
        x3 = self.res7(x)
        x4 = self.attention2(x)
        x = x3+x4

        x = self.conv6(x)
        x = self.bn6(x)
       

        pos_output = self.pos_output(x)
        cos_output = self.cos_output(x)
        sin_output = self.sin_output(x)
        width_output = self.width_output(x)

        return pos_output, cos_output, sin_output, width_output