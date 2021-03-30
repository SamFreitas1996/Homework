#HW 4 problem 1

import numpy as np 
import os
import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

import torch.nn as nn
import torch.nn.functional as nn_func
import torch.optim as optim


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=4,
                                          shuffle=True, num_workers=0)

testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=4,
                                         shuffle=False, num_workers=0)

classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')



class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 12, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(12, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(nn_func.relu(self.conv1(x)))
        x = self.pool(nn_func.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = nn_func.relu(self.fc1(x))
        x = nn_func.relu(self.fc2(x))
        x = self.fc3(x)
        return x



def imshow_custom(img,fig_number,fig_title):
    plt.ion()
    img = (img / 2 + 0.5).cpu()     # unnormalize
    npimg = img.numpy()
    fig_n = plt.figure(fig_number)
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.title(fig_title)
    fig_n.show()


net = Net()
net.to(device)

# get some random training images
dataiter = iter(trainloader)
images, labels = dataiter.next()

# print labels
this_title = (' '.join('%5s' % classes[labels[j]] for j in range(4)))
# show images
# imshow_custom(torchvision.utils.make_grid(images),1,this_title)

criterion = nn.CrossEntropyLoss()
# weight_decay is L2 nrom
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9,weight_decay=1e-2)


for epoch in range(2):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        # inputs, labels = data
        inputs, labels = data[0].to(device), data[1].to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % 2000 == 1999:    # print every 2000 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 2000))
            running_loss = 0.0

print('Finished Training')

PATH = './cifar_net.pth'
torch.save(net.state_dict(), PATH)


dataiter = iter(testloader)
images, labels = dataiter.next()
images, labels = images.cuda(), labels.cuda()

net = Net()
net.to(device)
PATH = './cifar_net.pth'
net.load_state_dict(torch.load(PATH))
outputs = net(images).to(device)


_, predicted = torch.max(outputs, 1)

this_title = ('Predicted: ', ' '.join('%5s' % classes[predicted[j]]
                              for j in range(4)))

# imshow_custom(torchvision.utils.make_grid(images),2,this_title)

correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data[0].to(device), data[1].to(device)
        outputs = net(images).to(device)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()


class_correct = list(0. for i in range(10))
class_total = list(0. for i in range(10))
with torch.no_grad():
    for data in testloader:
        images, labels = data[0].to(device), data[1].to(device)
        outputs = net(images)
        _, predicted = torch.max(outputs, 1)
        c = (predicted == labels).squeeze()
        for i in range(4):
            label = labels[i]
            class_correct[label] += c[i].item()
            class_total[label] += 1


for i in range(10):
    print('Accuracy of %5s : %2d %%' % (
        classes[i], 100 * class_correct[i] / class_total[i]))

print('Accuracy of the network on the 10000 test images: %d %%' % (
    100 * correct / total))


plt.ioff()
plt.show()
