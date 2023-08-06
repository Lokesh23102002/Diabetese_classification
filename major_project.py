# -*- coding: utf-8 -*-
"""Major_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Nv5MzBniPvS_HnMrTQaXzZLgxlnia8cW
"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import metrics
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import confusion_matrix,recall_score,accuracy_score as acc
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
# from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier as DTC
from sklearn.metrics import f1_score
from sklearn.model_selection import KFold
from sklearn.naive_bayes import BernoulliNB

"""# Pre-processing"""

from google.colab import drive
drive.mount('/content/drive')

# df=pd.read_csv('/content/drive/MyDrive/4th sem/PR-ML[3-0-2] - cmn/major project/diabetes_data.csv',sep=';')
df=pd.read_csv('/content/drive/MyDrive/major_project/diabetes_data.csv',sep=';')
print(df)

df['gender'].replace(['Male', 'Female'],[0, 1], inplace=True)

pd.unique(df['gender'])

df.head()

df.info()

"""#Train Test"""

# Choosing the features and the label
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

# train and test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

type(X_train)

encoder = MinMaxScaler()
X_train = encoder.fit_transform(X_train.values)
X_test = encoder.transform(X_test.values)


print(X_train)
print(X_test)

"""# Visualization"""

# import seaborn as sns
# import matplotlib.pyplot as plt

# sns.pairplot(df, hue='class', height=2)

# sns.scatterplot( x="polyuria",data=df,
#                 hue='class')
  
# # Placing Legend outside the Figure
# plt.legend(bbox_to_anchor=(1, 1), loc=2)
  
# plt.show()

type(X_train)

fig, axes = plt.subplots(4,4,sharey=True,figsize=(16,16))
fig.suptitle('countplot of various features')
for i,name in enumerate(df.drop(columns=["class","age"])):
  sns.countplot(ax=axes[int(i/4)][i%4],data=df, x=name, hue="class")

sns.histplot(data=df, x="age", hue="class", multiple="stack",kde=True)

"""# Logistic Regression"""

# X_train = X_train.to_numpy()

# Logistic Regression
classifier_lr = LogisticRegression(random_state=0)
classifier_lr.fit(X_train, y_train.values)

lr_test_score = classifier_lr.score(X_test, y_test)

"""## Five Fold Cross Validation"""

kfold = KFold(n_splits=5)
scores = cross_val_score(classifier_lr, X_train, y_train, cv=kfold)
print(scores.mean())

"""## Test accuracy"""

lr_test_score = classifier_lr.score(X_test, y_test)
lr_test_score*100

"""## f1_score"""

y_pred_logistic = classifier_lr.predict(X_test)
f1_score(y_test,y_pred_logistic)

"""## Recall"""

recall_score(y_test,y_pred_logistic)

print(classifier_lr.predict(X_test))
type(y_test)

"""#Neural Network

##Necessary libraries for neural network
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader,Dataset
import torchvision.transforms as transforms
import torchvision.datasets as datasets

"""## Dataset Preparation"""

class ddata(Dataset):
 
  def __init__(self,file_name):
    df=pd.read_csv(file_name,sep=';')
    df['gender'].replace(['Male', 'Female'],[0, 1], inplace=True)
    x=df.iloc[:,0:16].values
    y=df.iloc[:,-1].values
 
    self.x_train=torch.tensor(x,dtype=torch.float32)
    self.y_train=torch.LongTensor(y)
 
  def __len__(self):
    return len(self.y_train)
   
  def __getitem__(self,idx):
    return self.x_train[idx],self.y_train[idx]

dataset = ddata(file_name = '/content/drive/MyDrive/major_project/diabetes_data.csv')
train_set,test_set= torch.utils.data.random_split(dataset,[400,120])
train_loader = DataLoader(dataset = train_set, batch_size = 30,shuffle = True)
test_loader = DataLoader(dataset = test_set, batch_size = 10,shuffle = True)

print(train_set[0])

"""##Neural network making"""

class diabetese_classifier(nn.Module):
  def __init__(self,input_size , num_classes):
    super(diabetese_classifier,self).__init__()
    self.fc1 = nn.Linear(input_size,32)
    self.fc2 = nn.Linear(32,16)
    self.fc3 = nn.Linear(16,8)
    self.fc4 = nn.Linear(8,num_classes)

  def forward(self,x):
    x = F.sigmoid(self.fc1(x))
    x = F.sigmoid(self.fc2(x))
    x = F.sigmoid(self.fc3(x))
    out = F.sigmoid(self.fc4(x))
    return out

device = 'cpu'

input_size = 16
num_classes = 2
learning_rate = 0.01
batch_size = 60
num_epochs = 5

model = diabetese_classifier(input_size=input_size,num_classes=num_classes).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(),lr = learning_rate)

"""## train model"""

losse = []
for epoch in range(100):
  for index ,(data,targets) in enumerate(train_loader):
    data = data.to(device=device)
    targets = targets.to(device=device)

    scores = model(data)
    loss = criterion(scores,targets)
    optimizer.zero_grad()
    loss.backward()
    
    optimizer.step()
  losse.append(loss.item())

plt.plot(losse)
plt.xlabel("No of epochs")
plt.ylabel("Loss")

"""## Testing the neural net

"""

def check_accuracy(loader,model):
  num_correct = 0
  num_samples = 0
  y_pred =[]
  y_test = []
  model.eval()

  with torch.no_grad():
    for x,y in loader:
      x=x.to(device=device)
      y=y.to(device=device)
      y_test.append(list(y.numpy()))
      scores = model(x)
      #la = nn.Softmax(dim=1)
      # print(la(scores))
      _,predictions = scores.max(1)
      # print(predictions)
      y_pred.append(list(predictions.numpy()))
      num_correct += (predictions == y).sum()
      num_samples += predictions.size(0)

    print(f'Got{num_correct}/{num_samples} with accuracy {float(num_correct)/float(num_samples)*100}')
    return list(np.concatenate(y_pred).flat),list(np.concatenate(y_test).flat)
y_pred_nn,y_test_nn = check_accuracy(test_loader,model)
y_pred_tr=check_accuracy(train_loader,model)

"""### F1-score"""

f1_score(y_test_nn,y_pred_nn)

"""### recall score"""

recall_score(y_test_nn,y_pred_nn)

"""#SVM

##Train model
"""

svm_classifier = SVC(C=0.5)
svm_classifier.fit(X_train,y_train)

"""## Five fold cross_validation"""

kfold = KFold(n_splits=5)
scores = cross_val_score(svm_classifier, X_train, y_train, cv=kfold)
print(scores.mean()*100)

"""## Test accuracy"""

svm_score = svm_classifier.score(X_test, y_test)
svm_score

"""## F1 score"""

y_pred_svc = svm_classifier.predict(X_test)
f1_score(y_test,y_pred_svc)

"""##Recall Score"""

recall_score(y_test,y_pred_svc)

"""#Decision Tree classifier

## Train Model
"""

decision_tree_Classifier = DTC()
decision_tree_Classifier.fit(X_train,y_train)

"""## Five fold cross_validation"""

kfold = KFold(n_splits=5)
scores = cross_val_score(decision_tree_Classifier, X_train, y_train, cv=kfold)
print(scores.mean()*100)

"""## Test accuracy"""

decision_tree_score = decision_tree_Classifier.score(X_test, y_test)
decision_tree_score*100

"""## F1 Score"""

y_pred_DTC = decision_tree_Classifier.predict(X_test)
f1_score(y_test,y_pred_DTC)

"""## Recall Score"""

recall_score(y_test,y_pred_DTC)

"""#Random Forest Classifier

## Train Model
"""

Random_forest_classifier = RandomForestClassifier()
Random_forest_classifier.fit(X_train,y_train)

"""## Five fold cross_validation"""

kfold = KFold(n_splits=5)
scores = cross_val_score(Random_forest_classifier, X_train, y_train, cv=kfold)
print(scores.mean()*100)

"""## Test accuracy"""

Random_forest_score = Random_forest_classifier.score(X_test, y_test)
Random_forest_score*100

"""## F1 Score"""

y_pred_RFC = Random_forest_classifier.predict(X_test)
f1_score(y_test,y_pred_RFC)

"""## Recall Score"""

recall_score(y_test,y_pred_RFC)

"""#Bernoulli Naive bayes

## Train Model
"""

Naivebayes_classifier = BernoulliNB()
Naivebayes_classifier.fit(X_train,y_train)

"""## Five fold cross_validation"""

kfold = KFold(n_splits=5)
scores = cross_val_score(Naivebayes_classifier, X_train, y_train, cv=kfold)
print(scores.mean()*100)

"""## Test accuracy"""

Naivebayes_score = Naivebayes_classifier.score(X_test, y_test)
Naivebayes_score*100

"""## F1 Score

## Recall Score
"""

y_pred_NB = Naivebayes_classifier.predict(X_test)
f1_score(y_test,y_pred_NB)

recall_score(y_test,y_pred_NB)