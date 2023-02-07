import torch.nn as nn
import torch.nn.functional as F

from inference.models.grasp_model import GraspModel, MBC, ResidualBlockMish


class GenerativeResnet(GraspModel):

    def __init__(self, input_channels=1, dropout=False, prob=0.0, channel_size=32):
        super(GenerativeResnet, self).__init__()
        self.conv1 = nn.Conv2d(input_channels, channel_size, kernel_size=9, stride=1, padding=4)
        self.bn1 = nn.BatchNorm2d(32)
        self.act1 = nn.Mish(inplace=True)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.act2 = nn.Mish(inplace=True)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.act3 = nn.Mish(inplace=True)

        self.mbc1 = ResidualBlockMish(128, 128)
        self.mbc2 = ResidualBlockMish(128, 128)
        self.mbc3 = ResidualBlockMish(128, 128)
        self.mbc4 = MBC(128, 128)
        self.mbc5 = MBC(128, 128)
        self.mbc6 = MBC(128, 128)

        self.conv4 = nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1, output_padding=1)
        self.bn4 = nn.BatchNorm2d(64)
        self.act4 = nn.Mish(inplace=True)

        self.conv5 = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=2, output_padding=1)
        self.bn5 = nn.BatchNorm2d(32)
        self.act5 = nn.Mish(inplace=True)

        self.conv6 = nn.ConvTranspose2d(32, 32, kernel_size=9, stride=1, padding=4)

        self.pos_output = nn.Conv2d(32, 1, kernel_size=2)
        self.cos_output = nn.Conv2d(32, 1, kernel_size=2)
        self.sin_output = nn.Conv2d(32, 1, kernel_size=2)
        self.width_output = nn.Conv2d(32, 1, kernel_size=2)
        # self.dropout = dropout
        # self.dropout1 = nn.Dropout(p=prob)

        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.xavier_uniform_(m.weight, gain=1)

    def forward(self, x_in):
        x = self.act1((self.bn1(self.conv1(x_in))))
        x = self.act2(((self.bn2(self.conv2(x)))))
        x = self.act3(((self.bn3(self.conv3(x)))))
        x = self.mbc1(x)
        x = self.mbc2(x)
        x = self.mbc3(x)
        x = self.mbc4(x)
        x = self.mbc5(x)
        x = self.mbc6(x)
        x = self.act4((self.bn4(self.conv4(x))))
        x = self.act5((self.bn5(self.conv5(x))))
        x = self.conv6(x)

        # pos_output = self.pos_output(self.dropout1(x))
        # cos_output = self.cos_output(self.dropout1(x))
        # sin_output = self.sin_output(self.dropout1(x))
        # width_output = self.width_output(self.dropout1(x))
        
        pos_output = self.pos_output(x)
        cos_output = self.cos_output(x)
        sin_output = self.sin_output(x)
        width_output = self.width_output(x)

        return pos_output, cos_output, sin_output, width_output
