# -*- coding: utf-8 -*-
"""박규원

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yKg_xhP5nDmlhLNOl6U31ZY4Ho0urn1_
"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

"""신경망 변환
=============================


**Author**: `Alexis Jacq <https://alexis-jacq.github.io>`_
 
**Edited by**: `Winston Herring <https://github.com/winston6>`_
"""

from __future__ import print_function
#__future__모듈로부터 print_function 함수를 가져온다.

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
# 파이토치로 신경망 처리를 할 때 필수 패키지인 신경망을 torch.nn 패키지로 생성한다.
# 효과적인 그라디언트 디센트인 torch.optim을 가져온다.

from PIL import Image
# 이미지를 읽고 보여주는 패키지인 PIL(파이썬 이미지 라이브러리)로부터 이미지를 가져온다.
import matplotlib.pyplot as plt
# 파이썬에서 자료를 차트나 플롯으로 시각화하는 패키지인 Matplotlib를 가져온다.
import torchvision.transforms as transforms
# PIL타입의 이미지들을 토치 텐서 형태로 변형해주는 패키지를 가져온다.
import torchvision.models as models
# 사전 훈련된 모델들의 학습 또는 읽기 패키지인 torchvision.models를 가져온다.

import copy
#모델을 복사하기 위한 패키지인 copy를 가져온다.

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#CUDA(Compute Unified Device Architecture)는 GPU(그래픽 처리 장치)에서 수행하는 알고리즘을 
#다양한 언어로 작성할 수 있도록 하는 GPGPU(General-Purpose computing on Graphics Processing Units), 
#즉 GPU 상의 범용 계산이다.
#CUDA를 사용하기 위해서는 파이토치에서 torch.cuda.is_avialbavle()를 사용해야한다.
#해당 컴퓨터에서 GPU 사용이 가능하면 "True"를 반환한다.
#GPU 사용이 불가하면 후에 else값인 "cpu"를 반환할 것이다.

# 출력 이미지의 원하는 크기를 정하는 과정이다.
imsize = 512 if torch.cuda.is_available() else 128  
# 만약 GPU 사용이 가능하면, 512 사이즈를 사용하고, GPU 사용이 불가하면 128사이즈를 사용한다.

loader = transforms.Compose([ 
    # 데이터를 normalization시키기 위해서 transforms.Compose를 사용한다.
    # compose는 여러 transform들을 chaining한다.
    # 여러 transform을 진행한다.
    transforms.Resize(imsize),  # 입력 영상의 크기를 맞춘다.
    transforms.ToTensor()])  
    # 데이터 타입을 토치 텐서 형태로 변환한다.
    # 이 때 토치 텐서 형태로 변환하면 0에서 1의 값으로 변환된다.


def image_loader(image_name):
# image_name을 매개변수로 하여 image_loader라는 함수를 만드는 과정이다. 
    image = Image.open(image_name)
    image = loader(image).unsqueeze(0)
    # 네트워크의 입력 차원을 맞추기 위해 필요한 가짜 배치 차원이다.
    # unsqueeze()함수는 차원을 변환하는 함수로, 인수로 받은 위치에 새로운 차원을 삽입한다.

 
  return image.to(device, torch.float)
  # float형의 tensor를 반환한다.
  


style_img = image_loader("./images/picasso.jpg") # style image에 피카소의 작품을 대입한다.
content_img = image_loader("./images/dancing.jpg") # content image에 dancing이라는 이미지를 대입한다.

assert style_img.size() == content_img.size(), \
# assert는 방어적 프로그램 방식으로, 어떤 조건의 참임을 보증하거나, 
# 함수의 반환값이 어떤 조건에 만족하도록 만들 수 있다.
# 현재 상황에서는 style image와 content image의 사이즈를 같게 만드는 것을 의도한다.

unloader = transforms.ToPILImage()  # PIL(파이썬 이미지 라이버러리) 이미지로 재변환한다.

plt.ion()

def imshow(tensor, title=None): #imshow()함수는 이미지를 사이즈에 맞게 보여준다.
    image = tensor.cpu().clone()  # 기존의 텐서를 복제하여 텐서 값에 변화가 적용되지 않도록 한다.
    image = image.squeeze(0)      # squeeze() 함수는 차원을 줄이는 함수이다.
    # 이전에 입력차원을 맞추기 위해 unsqueeze해주었던 가짜 배치 차원을 squeeze하여 가짜 배치 차원을 제거한다.
    image = unloader(image)
    plt.imshow(image)
    if title is not None: # title이 None이 아니라면
        plt.title(title)
    plt.pause(0.001) # pause 함수를 통해 업데이트가 되는 시간을 위해 잠시 멈춘다.


plt.figure()
imshow(style_img, title='Style Image') # Style lmage를 사이즈에 맞게 보여준다.

plt.figure()
imshow(content_img, title='Content Image') # Content lmage를 사이즈에 맞게 보여준다.

class ContentLoss(nn.Module): # 콘텐츠 로스

    def __init__(self, target,):
        #__init__메소드는 인스턴스 생성 초기에 변수를 지정하는 것을 도와준다.
        super(ContentLoss, self).__init__()
        # ContentLoss 클래스를 사용하기 위해서 super()함수를 사용한다.
        # 그라디언트를 동적으로 계산하는 데 사용되는 트리에서 대상 콘텐츠를 contentloss하는 과정이다.
        # 이 값은 변수가 아니라 명시된 값이다.
        self.target = target.detach()

    def forward(self, input): # 입력값을 반환하는 forward 메소드를 만들어야 한다.
        self.loss = F.mse_loss(input, self.target)
        return input # 계산된 로스인 입력값을 반환한다.

def gram_matrix(input):
  # 스타일 로스를 하기 전에 gram 생성을 계산하는 모듈을 먼저 정의해야 한다.
    a, b, c, d = input.size()  
    # a=배치 크기(=1)
    # b=특징 맵의 크기
    # (c,d)=특징 맵(N=c*d)의 차원

    features = input.view(a * b, c * d)  # F_XL을 \hat F_XL로 크기 조정한다

    G = torch.mm(features, features.t())  # 텐서 연산 중 내적을 구하는 torch.mm을 통해 그램 곱을 수행한다

    # 그램 행렬의 값을 각 특징 맵의 요소 숫자로 나누는 방식으로 영역을 지정하여 '정규화'를 수행한다.
    return G.div(a * b * c * d)

class StyleLoss(nn.Module): # 스타일 로스
  # 스타일로스는 콘텐츠 로스와 형식과 모듈이 거의 일치하지만, 변수나 대상 등에서 약간의 차이가 있다.

    def __init__(self, target_feature):
        super(StyleLoss, self).__init__()
        self.target = gram_matrix(target_feature).detach()

    def forward(self, input): # 입력값을 반환하는 forward 메소드를 만들어야 한다.
        G = gram_matrix(input)
        self.loss = F.mse_loss(G, self.target)
        return input # 계산된 로스인 입력값을 반환한다.

cnn = models.vgg19(pretrained=True).features.to(device).eval()
# 19 레이어 층을 가지는 VGG(VGG19) 네트워크를 사전 훈련된 네트워크로 사용한다.
# CNN을 통해 각각의 특징을 계층적으로 쌓으면서, 더 높은 층으로 갈 수록 더 좋은 결과를 출력할 수 있다.

cnn_normalization_mean = torch.tensor([0.485, 0.456, 0.406]).to(device)
cnn_normalization_std = torch.tensor([0.229, 0.224, 0.225]).to(device)
# VGG 네트워크는 평균 = [0.485, 0.456, 0.406] 및 표준편차 = [0.229, 0.224, 0.225]로 정규화 된 각 채널의 이미지에 대해 학습된 모델
# VGG 네트워크를 사용하므로 입력 이미지를 네트워크로 보내기 전에 정규화 하는데 위 평균과 표준편차 값을 사용합니다.

class Normalization(nn.Module):
    def __init__(self, mean, std):
        super(Normalization, self).__init__()
        # 바로 입력 이미지 텐서의 모양인 [B x C x H x W] 에 연산할 수 있도록 만들어야 한다.
        # B = 배치 크기, C = 채널 값, H = 높이, W = 넓이
        # Normalization 클래스를 사용하기 위해서 super()함수를 사용한다.
      
        self.mean = torch.tensor(mean).view(-1, 1, 1)
        # 텐서의 모양을 바꾸는 view함수로 평균 텐서를 [C x 1 x 1] 형태로 만든다.
        self.std = torch.tensor(std).view(-1, 1, 1)
        # 텐서의 모양을 바꾸는 view함수로 표준편차 텐서를 [C x 1 x 1] 형태로 만든다.

        
    def forward(self, img):
        # img 값을 정규화(normalize)한다.
        return (img - self.mean) / self.std

# 스타일/콘텐츠 로스로 계산하길 원하는 깊이의 레이어들:
content_layers_default = ['conv_4']
style_layers_default = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']

def get_style_model_and_losses(cnn, normalization_mean, normalization_std,
                               style_img, content_img,
                               content_layers=content_layers_default,
                               style_layers=style_layers_default):
    cnn = copy.deepcopy(cnn)
    # CNN을 통해 각각의 특징을 계층적으로 쌓으면서, 더 높은 층으로 갈 수록 더 좋은 결과를 출력할 수 있다.
    # cnn, 표준화된 평균, 표준화된 표준편차, 스타일 이미지, 컨텐츠 이미지,
    # 콘텐츠 로스로 계산하길 원하는 깊이의 레이어, 스타일 로스로 계산하길 원하는 깊이의 레이어등을 포함하여 함수를 만든다.

    
    # 표준화(normalization) 모듈
    # 표준화된 평균과 표준화된 표준 편차를 표준화하여 디바이스에 넣는다.
    normalization = Normalization(normalization_mean, normalization_std).to(device)

    # 단지 반복 가능한 접근을 갖거나 콘텐츠/스타일의 리스트를 갖기 위함이다.
    # 로스값
    content_losses = []
    style_losses = []

    # cnn은 nn.Sequential 하다고 가정하므로, 새로운 nn.Sequential을 만든다.
    # nn.Sequential은 다른 모듈들을 포함하는 모듈이다. 
    # nn.Sequential은 모듈들을 순차적으로 적용하여 출력을 생성한다.
    # 순차적으로 활성화 하고자하는 모듈들을 넣는다.
    model = nn.Sequential(normalization)

    i = 0  # i의 초기값을 0으로 설정하고, conv레이어를 찾을때마다 값을 증가 시킨다.
    for layer in cnn.children():
        if isinstance(layer, nn.Conv2d): # 레이어가 컨볼루젼 레이어 2d 상태일 때
            i += 1 # i의 값에서 i을 추가한다.
            name = 'conv_{}'.format(i)
        elif isinstance(layer, nn.ReLU): # 레이어가 Relu일 때
            name = 'relu_{}'.format(i)
            # in-place(입력 값을 직접 업데이트) 버전은 콘텐츠로스와 스타일로스에 좋은 결과를 보여줄 수 없다.
            layer = nn.ReLU(inplace=False)  # 그래서 여기선 out-of-place로 대체하기 위해 inplace를 False로 둔다.
        elif isinstance(layer, nn.MaxPool2d):
            name = 'pool_{}'.format(i)
        elif isinstance(layer, nn.BatchNorm2d):
            name = 'bn_{}'.format(i)
        else:
            raise RuntimeError('Unrecognized layer: {}'.format(layer.__class__.__name__))

        model.add_module(name, layer)

        if name in content_layers:
            # 콘텐츠 로스 추가:
            target = model(content_img).detach()
            content_loss = ContentLoss(target)
            model.add_module("content_loss_{}".format(i), content_loss)
            content_losses.append(content_loss)

        if name in style_layers:
            # 스타일 로스 추가:
            target_feature = model(style_img).detach()
            style_loss = StyleLoss(target_feature)
            model.add_module("style_loss_{}".format(i), style_loss)
            style_losses.append(style_loss)

    # 마지막 콘텐츠 및 스타일 로스 이후의 레이어들을 잘라낸다.
    for i in range(len(model) - 1, -1, -1):
        if isinstance(model[i], ContentLoss) or isinstance(model[i], StyleLoss): # 컨텐츠 로스나 스타일 로스를 한 상태라면,
            break # 탈출

    model = model[:(i + 1)]

    return model, style_losses, content_losses # 모델과 스타일 로스값과 컨텐츠 로스값을 반환한다.

input_img = content_img.clone() # 이미지를 입력하는 과정이다.
# 대신에 백색 노이즈를 이용하길 원한다면 아래 줄의 주석처리를 제거해야 한다.:
# input_img = torch.randn(content_img.data.size(), device=device)
# randn : 가우시안 표준 정규 분포

# 원본 입력 이미지를 창에 추가한다:
plt.figure()
imshow(input_img, title='Input Image') # 사이즈에 맞춰 입력받은 이미지를 출력한다.

def get_input_optimizer(input_img):
    # 이 줄은 입력은 그레이던트가 필요한 파라미터라는 것을 보여주기 위해 존재한다.
    # .requires_grad_()를 사용하여 해당 이미지가 그라디언트가 필요함을 확실하게 한다.
    optimizer = optim.LBFGS([input_img.requires_grad_()])
    return optimizer # 옵티마이저를 반환한다.

def run_style_transfer(cnn, normalization_mean, normalization_std,
                       content_img, style_img, input_img, num_steps=300,
                       style_weight=1000000, content_weight=1):
    """스타일 변환을 실행한다."""
    print('Building the style transfer model..')
    model, style_losses, content_losses = get_style_model_and_losses(cnn,
        normalization_mean, normalization_std, style_img, content_img)
    optimizer = get_input_optimizer(input_img)

    print('Optimizing..')
    run = [0]
    while run[0] <= num_steps:

        def closure():
            # 입력 이미지의 업데이트된 값들을 보정한다.
            # 옵티마이저는 인수로서 클로저를 필요로 한다.
            input_img.data.clamp_(0, 1)

            optimizer.zero_grad()
            model(input_img)
            style_score = 0 # 스타일 스코어 값을 0으로 초기화해둔다.
            content_score = 0 # 컨텐츠 스코어 값을 0으로 초기화해둔다.

            for sl in style_losses: #스타일 로스가 일어날 때까지,
                style_score += sl.loss # 기존의 스타일 스코어 값에 스타일 로스 값을 더한다.
            for cl in content_losses: # 콘텐츠 로스가 일어날 때까지, 
                content_score += cl.loss # 기존의 콘텐츠 스코어 값에 콘텐츠 로스 값을 더한다.

            style_score *= style_weight 
            content_score *= content_weight

            loss = style_score + content_score
            loss.backward()
            # 그라디언트를 동적으로 계산하고 그라디언트 디센트 단계를 수행하기 위해 backword 메소드를 실행한다.

            run[0] += 1
            if run[0] % 50 == 0:
                print("run {}:".format(run))
                print('Style Loss : {:4f} Content Loss: {:4f}'.format(
                    style_score.item(), content_score.item()))
                print()

            return style_score + content_score

        optimizer.step(closure)

    # 마지막 보정
    input_img.data.clamp_(0, 1) 
    # clamp 함수를 통해 정해진 범위인 0-1 사이의 값을 유지하도록 고정시킨다.

    return input_img

# 마지막 알고리즘 실행
output = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std,
                            content_img, style_img, input_img)

plt.figure()
imshow(output, title='Output Image') # 마지막 결과인 출력 이미지를 사이즈에 맞게 보여준다.

# sphinx_gallery_thumbnail_number = 4
plt.ioff() # ioff는 interactive-off로, 여기서 그림에 관련된 모든 명령을 실행한다.
plt.show() # 여기서 최종적으로 그림을 보여준다.

# 원 코드
# https://tutorials.pytorch.kr/advanced/neural_style_tutorial.html

# 참고 사이트
# https://medium.com/pytorch-forever/pytorch-%E1%84%8B%E1%85%B5%E1%84%86%E1%85%B5%E1%84%8C%E1%85%B5-%E1%84%87%E1%85%AE%E1%86%AB%E1%84%85%E1%85%B2-%E1%84%92%E1%85%A2%E1%84%87%E1%85%A9%E1%84%80%E1%85%B5-4ceab523cb66
# https://datascienceschool.net/view-notebook/f43be7d6515b48c0beb909826993c856/
# https://wikidocs.net/21050
# https://opencv-python.readthedocs.io/en/latest/doc/01.imageStart/imageStart.html
# https://wikidocs.net/28
# https://rednooby.tistory.com/54
# http://sanghyukchun.github.io/92/
# https://tutorials.pytorch.kr/beginner/examples_nn/two_layer_net_nn.html
# https://code-examples.net/ko/q/28e59db