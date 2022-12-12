from torch import nn

class CNNetwork(nn.Module):

    def __init__(self):
        super().__init__()
        # 4 conv blocks / flatten / linear / softmax
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=16,
                kernel_size=3,
                stride=1,
                padding=2
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(
                in_channels=16,
                out_channels=32,
                kernel_size=3,
                stride=1,
                padding=2
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(
                in_channels=32,
                out_channels=64,
                kernel_size=3,
                stride=2,
                padding=2
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(
                in_channels=64,
                out_channels=128,
                kernel_size=3,
                stride=2,
                padding=2
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )
        self.flatten = nn.Flatten()
        self.linear1 = nn.Linear(512,256)
        self.linear2 = nn.Linear(256,1)
        self.output = nn.Sigmoid()

    def forward(self, input_data): 
        
                           #pour 1 sec:        pour 2 sec:
        x = self.conv1(input_data)    #after conv1 -> [3,16,64,17]         [3, 16, 33, 32] 
        #print(x.size())   
        x = self.conv2(x)           #after conv2  -> [3,32,17,9]           [3, 32, 17, 17]
        #print(x.size())   
        x = self.conv3(x)         # after conv3 -> [3,64,5,3]              [3, 64, 5, 5]
        #print(x.size())   
        x = self.conv4(x)       # after conv4 size -> [3,128,2,1]          [3, 128, 2, 2]
        #x = input_data.view(x.size(0), -1)
        x = self.flatten(x)    # after flatten size -> [3,256]             [3, 512]
        #print(x.size())   
        logits = self.linear1(x)   # after linear size -> [3,1]
        logits = self.linear2(logits)
        #print(logits.size())   
        predictions = self.output(logits)
        return predictions

 
#f __name__ == "__main__":
#    cnn = CNNNetwork()
#    summary(cnn.cuda(), (1, 64, 32)