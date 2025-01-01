# -*- coding: utf-8 -*-
"""da-assgn-1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1f_Oki_uXm2XHKpMiZ9FpFoyYFSPCME7v

# Data Analytics (CS61061), Autumn 2024
### Assignment 1
#### Team Members:
* Hardik Soni (20CS30023)
* Astitva (20CS30007)
* Sake Venkata Vighan Kumar (20CS10052)

# Part A:- Exploratory Data Analysis (EDA) : Unveiling Patterns in Suspect Identification Data
## Understanding the data
"""

# !pip install pycountry

# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry
from scipy import stats
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

"""### Load the dataset into pandas dataframe
Let's start by importing our data. (**Note**: Change the File Path according to your environment and the location of the *.csv file)
"""

file_path = '/kaggle/input/suspect-synthetic-data/Dataset.csv'
df = pd.read_csv(file_path)
df

df.info()

"""## Fill Missing Values

The ```df.info()``` method aboves provides us with a concise saummary of a Pandas Dataframe. Here we can observe the **Data Type (Dtype)** of each feature. Another point to be noted is that the features with name **maritalstatus, race, sex, hoursperweek** have null values.
"""

# Sample 500 rows and compute mode for missing categorical columns
modes = df.sample(n=500, random_state=42)[['maritalstatus', 'race', 'sex']].mode().iloc[0]

# Fill missing values with the mode and interpolate 'hoursperweek'
df.fillna(modes, inplace=True)
df['hoursperweek'].interpolate(method='pchip', inplace=True)

# Convert 'Possibility' to 0/1 based on its string values
df['Possibility'] = df['Possibility'].map({'<=0.5': 0, '>0.5': 1})

"""The missing values in the dataset are handled using a combination of mode imputation and interpolation:

1. ***Sampling***: A random sample of 500 rows is drawn from the dataset to ensure that the mode calculation is representative while maintaining randomness.
2. ***Mode Imputation***: The mode (most frequent value) of the sampled data is computed for each categorical column with missing values (*maritalstatus, race, sex*). The missing values in these columns are then filled with their respective modes.
3. ***Interpolation***: Missing values in the *hoursperweek* column, which is continuous, are filled using Piecewise Cubic Hermite Interpolation (```pchip```), which provides a smooth estimate between known data points.
"""

convert_dict = {'age': 'int8',
                'workclass': 'category',
                'education': 'category',
                'educationno': 'int8',
                'maritalstatus': 'category',
                'occupation': 'category',
                'relationship': 'category',
                'race': 'string',
                'sex': 'category',
                'capitalgain': 'int32',
                'capitalloss': 'int32',
                'hoursperweek': 'int8',
                'native': 'category',
                'Possibility': 'int8'}
df = df.astype(convert_dict)

df.info()

df.describe()

# A sample of the data after data types changes
df.sample(10)

"""As we see in the latest results, we can greatly reduce the memory size of our DataFrame by changing the data types and downcasting integers and floats. Please note that **these steps can be optional**, but can be very useful if we’re working with a large dataset.

## Analyzing and Visualizing the Data
### Category Distribution and Univariate Correlation Analysis
"""

# List of categorical features to plot
features_to_plot = ['workclass', 'education', 'maritalstatus',
                    'occupation', 'relationship', 'race']

# Set the plot size
plt.figure(figsize=(20, 18))

# Create subplots
for i, feature in enumerate(features_to_plot, 1):
    plt.subplot(3, 2, i)  # Adjust subplot grid based on the number of features
    sns.countplot(y=feature, data=df, hue='Possibility',
                  order=df[feature].value_counts().index, palette='viridis')
    plt.title(f'Distribution of {feature} by Possibility')
    plt.xlabel('Count')
    plt.ylabel(feature)

# Adjust layout
plt.tight_layout()
plt.show()

native_counts = df['native'].value_counts().reset_index()
native_counts.columns = ['Country', 'Count']
# Function to get ISO 3166-1 alpha-3 code
def get_country_code(name):
    # Special cases and known issues
    name_mapping = {
        'United-States': 'USA',
        'Puerto-Rico': 'PRI',
        'Dominican-Republic': 'DOM',
        'South': 'ZAF',  # assuming it refers to South Africa
        'Columbia': 'COL',  # corrected to Colombia
        'Outlying-US(Guam-USVI-etc)': 'GUM',  # Guantanamo Bay
        'Hong': 'HKG',  # assuming Hong Kong
        'Trinadad&Tobago': 'TTO',
        'Yugoslavia': 'YUG',  # deprecated, but code exists
        'Laos': 'LAO',
        'Cambodia': 'KHM',
        'Thailand': 'THA',
        'Scotland': 'GBR'  # part of the UK
    }
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return name_mapping.get(name, 'Unknown')

# Apply the function to get country codes
native_counts['Country_code'] = native_counts['Country'].apply(lambda x: get_country_code(x) or 'Unknown')

# Filter out any rows with unknown country codes
native_counts = native_counts[native_counts['Country_code'] != 'Unknown']

# Define color intervals
bins = [0, 10, 20, 50, 100, 200, 650, 30000]  # Define bins according to the count values
labels = ['0-10', '11-20', '21-50', '51-100', '101-200', '200-650', '650+']

native_counts['Count_bins'] = pd.cut(native_counts['Count'], bins=bins, labels=labels)

# Create the choropleth map with improved color scheme and actual count in pop-up
fig = px.choropleth(
    native_counts,
    locations='Country_code',
    color='Count_bins',
    hover_name='Country',
    hover_data={'Count': True, 'Count_bins': True},  # Show actual count and hide bins in hover
    color_discrete_map={
        '0-10': 'lightyellow',
        '11-20': 'lightgreen',
        '21-50': 'lightblue',
        '51-100': 'orange',
        '101-200': 'blue',
        '200-650': 'purple',
        '650+': 'darkblue'
    },
    labels={'Count': 'Number of Individuals', 'Country': 'Country'},
)
# Adjust the layout for height and width
fig.update_layout(
    title={'text': 'Geographical Distribution of \'native\' Countries', 'x': 0.5, 'xanchor': 'center'},
    height=800,  # Set height
    width=1600,  # Set width
    font=dict(
        family="Arial",
        size=16,
        color="Gray"
    ),
    title_font=dict(
        family="Roboto",
        size=24,
        color="Black"
    )
)
# Show the figure
fig.show()

g = sns.FacetGrid(df, hue='Possibility', height=7.5, aspect=2)
g.map(sns.histplot, 'age', kde=True).add_legend()
g.set_axis_labels('Age', 'Density')
g.set_titles('Distribution of Age by Possibility')
plt.show()

features = ['hoursperweek', 'educationno']

# Set up the matplotlib figure and axes
fig, axes = plt.subplots(1, 2, figsize=(15, 6))  # 1x2 grid for subplots

# Flatten the axes array for easy iteration
axes = axes.flatten()

# Loop through the features and plot each one
for i, feature in enumerate(features):
    sns.boxplot(x='Possibility', y=feature, data=df, ax=axes[i], palette='Set2')
    axes[i].set_title(f'Box Plot of $\mathbf{{{feature}}}$ by Possibility')

# Adjust layout for better spacing
plt.tight_layout()
plt.show()

proportions = pd.crosstab(df['sex'], df['Possibility'], normalize='index')

# Set up the matplotlib figure with a 2x3 grid
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(2, 3, width_ratios=[1, 0.5, 0.5], height_ratios=[1, 1], wspace=0.4, hspace=0.4)

# Create the heatmap in the first column, adjusting its height to be equal to its width
ax0 = fig.add_subplot(gs[:, 0])
sns.heatmap(proportions, annot=True, cbar=True, fmt='.2f', ax=ax0)
ax0.set_xlabel('Possibility', fontsize=12)
ax0.set_ylabel('Sex', fontsize=12)
ax0.set_title(r'Proportions of $\mathbf{Sex}$ by Possibility', fontsize=14)

# Adjust the heatmap aspect ratio
ax0.set_aspect('equal')

# Define the plot parameters
plot_params = [
    ('capitalgain', 'orange', 'Capital Gain Distribution for Possibility 0', 0, fig.add_subplot(gs[0, 1])),
    ('capitalgain', 'purple', 'Capital Gain Distribution for Possibility 1', 1, fig.add_subplot(gs[0, 2])),
    ('capitalloss', 'orange', 'Capital Loss Distribution for Possibility 0', 0, fig.add_subplot(gs[1, 1])),
    ('capitalloss', 'purple', 'Capital Loss Distribution for Possibility 1', 1, fig.add_subplot(gs[1, 2]))
]

# Loop through the plot parameters
for var, color, title, possibility, ax in plot_params:
    sns.violinplot(x='Possibility', y=var, data=df[df['Possibility'] == possibility], ax=ax, palette=[color])
    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Possibility', fontsize=12)
    ax.set_ylabel(var.replace('capital', 'Capital ').title(), fontsize=12)
    ax.set_xticklabels([str(possibility)])
    ax.grid(True, linestyle='--', linewidth=0.5)

# Adjust layout to ensure proper spacing
plt.tight_layout()
plt.show()

"""### Multivariate Correlation Analysis
Multivariate correlation analysis examines the relationships between multiple variables simultaneously. This often involves creating a correlation matrix and visualizing it using a heatmap.
"""

# List of categorical columns
categorical_cols = ['workclass', 'education', 'maritalstatus', 'occupation', 'relationship', 'race', 'sex', 'native']
df_label = df.copy()
# Apply LabelEncoder to each categorical column and store encoders
label_encoders = {col: LabelEncoder().fit(df[col]) for col in categorical_cols}
# Transform categorical columns using the fitted encoders
df_label[categorical_cols] = df[categorical_cols].apply(lambda col: label_encoders[col.name].transform(col))
corr_matrix = df_label.corr()
# Visualize the correlation matrix
plt.figure(figsize=(20, 20))
# Create the heatmap
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', square=True, linewidths=0.5, cbar_kws={"shrink": .75})
# Add a title
plt.title("Multivariate Correlation Matrix Heatmap\n", fontsize=20)
# Show the plot
plt.show()

"""Based on the initial heatmap analysis, the following features have been identified as potentially influential in determining the likelihood of someone being a criminal suspect:

1. **age**
2. **educationno**
3. **sex**
4. **capitalgain**
5. **capitalloss**
6. **hoursperweek**

### Basic Wrangling to Improve Accuracy of Models
Note: If you wish to see the difference in accuracy with and without wrangling, just comment the wrangle function and it's call in the cell below.
"""

def wrangle(df):
    """
    Filters the dataset by applying specific wrangling rules:
    1. Removes rows where 'age' exceeds 80.
    2. Filters out rows where categorical columns have unique values and 'Possibility' is 0.

    Parameters:
    df (DataFrame): The input DataFrame to be wrangled.

    Returns:
    DataFrame: The filtered DataFrame.
    """

    # Remove rows where 'age' is greater than 80
    mask_age = df['age'] <= 80

    # Define categorical columns to check for unique values
    cols = ['workclass', 'occupation', 'relationship', 'race']

    # Compute counts of unique values in categorical columns and add 'Possibility'
    counts = df[cols + ['Possibility']].groupby(cols).size().reset_index(name='count')

    # Identify categorical rows with only one occurrence
    singles = counts[counts['count'] == 1]

    # Create mask to filter out rows where categorical values are unique and 'Possibility' is 0
    mask_cat = ~(
        df[cols].merge(singles, how='left', on=cols, indicator=True)['_merge'] == 'both'
    ) | (df['Possibility'] != 0)

    # Apply masks to filter the DataFrame
    df_filtered = df[mask_age & mask_cat]

    return df_filtered

df = wrangle(df)
df

"""# Part B:- Implementing Naive Bayes from Scratch: A Custom Approach to Suspect Identification"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, ClassifierMixin
from scipy.stats import multivariate_normal as mvn
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, precision_recall_curve
ensemble_clf = []
acc_clf = {}
report_clf = {}
roc_area = {}

class GaussianNaiveBayes(BaseEstimator, ClassifierMixin):
    def __init__(self):
        self.class_priors = {}
        self.likelihoods = {}

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        self.num_features_ = X.shape[1]

        # Initialize likelihoods
        self.likelihoods = {c: [] for c in self.classes_}

        # Calculate class priors
        self.class_priors = {c: np.mean(y == c) for c in self.classes_}

        # Calculate mean and variance for each feature per class
        for c in self.classes_:
            X_c = X[y == c]
            means = np.mean(X_c, axis=0)
            variances = np.var(X_c, axis=0)
            self.likelihoods[c] = (means, variances)

        return self

    def predict(self, X):
        results = []

        for i in range(X.shape[0]):
            query = X[i]
            probs = {}

            for c in self.classes_:
                prior = self.class_priors[c]
                means, variances = self.likelihoods[c]
                likelihood = 1

                for j in range(self.num_features_):
                    mean = means[j]
                    var = variances[j]
                    if var > 0:
                        likelihood *= (1 / math.sqrt(2 * math.pi * var)) * np.exp(-(query[j] - mean) ** 2 / (2 * var))
                    else:
                        likelihood *= 1e-10

                probs[c] = likelihood * prior

            result = max(probs, key=probs.get)
            results.append(result)

        return np.array(results)

    def predict_proba(self, X):
        probas = []

        for i in range(X.shape[0]):
            query = X[i]
            probs = np.zeros(len(self.classes_))

            for idx, c in enumerate(self.classes_):
                prior = self.class_priors[c]
                means, variances = self.likelihoods[c]
                likelihood = 1

                for j in range(self.num_features_):
                    mean = means[j]
                    var = variances[j]
                    if var > 0:
                        likelihood *= (1 / math.sqrt(2 * math.pi * var)) * np.exp(-(query[j] - mean) ** 2 / (2 * var))
                    else:
                        # Avoid zero variance, assign a very small value to avoid zero probabilities
                        likelihood *= 1e-10

                probs[idx] = likelihood * prior

            # Check for NaNs and handle them
            if np.any(np.isnan(probs)) or np.all(probs == 0):
                probs = np.zeros(len(self.classes_))
                probs[0] = 1.0

            # Normalize probabilities to sum to 1
            probs /= probs.sum()
            probas.append(probs)

        return np.array(probas)

# Define the categorical columns
categorical_cols = ['workclass', 'education', 'maritalstatus', 'occupation', 'relationship', 'race', 'sex', 'native']

# Define the numerical columns
numerical_cols = ['age', 'educationno', 'capitalgain', 'capitalloss', 'hoursperweek']

# Create a ColumnTransformer with OneHotEncoder for categorical columns and StandardScaler for numerical columns
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_cols),
        ('num', StandardScaler(), numerical_cols)
    ],
    remainder='passthrough'  # Ensure all columns are processed
)

# Create a pipeline
model_pipeline_nv = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', GaussianNaiveBayes())
])

# Separate features and labels
X = df.drop(columns=['Possibility'])
y = df['Possibility']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Train the model
model_pipeline_nv.fit(X_train, y_train)

# Predict on the test set
y_pred_ori = model_pipeline_nv.predict(X_test)

# Evaluate the model
accuracy = 100 * accuracy_score(y_test, y_pred_ori)
cr = classification_report(y_test, y_pred_ori)
print(f"Accuracy: {accuracy:.3f} %.\n")
print("Classification Report:\n", cr)

ensemble_clf.append(model_pipeline_nv)
acc_clf['nb_m'] = accuracy
report_clf['nb_m'] = classification_report(y_test, y_pred_ori, output_dict=True)

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred_ori)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Innocent', 'Suspect'], yticklabels=['Innocent', 'Suspect'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ROC Curve
y_prob = model_pipeline_nv.predict_proba(X_test)[:, 1]  # Probabilities for the positive class
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
roc_area['nb_m'] = roc_auc
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)

plt.figure()
plt.plot(recall, precision, color='blue', lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.show()

"""# Part C:- Comparative Analysis of Custom and Sklearn-Based Classifiers for Suspect Identification

## Gaussian Naive-Bayes Algorithm
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, precision_recall_curve

# Create a ColumnTransformer with OneHotEncoder for categorical columns and StandardScaler for numerical columns
preprocessor_nb = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_cols),
    ],
    remainder='passthrough'  # Ensure all columns are processed
)
# Create a pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor_nb),
    ('classifier', GaussianNB())
])
# Train the model
model_pipeline.fit(X_train, y_train)

# Predict on the test set
y_pred = model_pipeline.predict(X_test)

# Evaluate the model
accuracy = 100 * accuracy_score(y_test, y_pred)
cr = classification_report(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f} %.\n")
print("Classification Report:\n", cr)

ensemble_clf.append(model_pipeline)
acc_clf['nb'] = accuracy
report_clf['nb'] = classification_report(y_test, y_pred, output_dict=True)

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Innocent', 'Suspect'], yticklabels=['Innocent', 'Suspect'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ROC Curve
y_prob = model_pipeline.predict_proba(X_test)[:, 1]  # Probabilities for the positive class
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
roc_area['nb'] = roc_auc
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)

plt.figure()
plt.plot(recall, precision, color='blue', lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.show()

"""## Support Vector Classifier (SVC)"""

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
import matplotlib.pyplot as plt

# Create a pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', SVC(kernel='linear', probability=True, random_state=42))
])
# Train the model
model_pipeline.fit(X_train, y_train)

# Predict on the test set
y_pred = model_pipeline.predict(X_test)

# Evaluate the model
accuracy = 100 * accuracy_score(y_test, y_pred)
cr = classification_report(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f} %.\n")
print("Classification Report:\n", cr)

ensemble_clf.append(model_pipeline)
acc_clf['svc'] = accuracy
report_clf['svc'] = classification_report(y_test, y_pred, output_dict=True)

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Innocent', 'Suspect'], yticklabels=['Innocent', 'Suspect'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ROC Curve
y_prob = model_pipeline.predict_proba(X_test)[:, 1]  # Probabilities for the positive class
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
roc_area['svc'] = roc_auc
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)

plt.figure()
plt.plot(recall, precision, color='blue', lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.show()

"""## K-Nearest Neighbours (kNN)"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
import matplotlib.pyplot as plt

# Create a pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', KNeighborsClassifier())
])
# Train the model
model_pipeline.fit(X_train, y_train)

# Predict on the test set
y_pred = model_pipeline.predict(X_test)

# Evaluate the model
accuracy = 100 * accuracy_score(y_test, y_pred)
cr = classification_report(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f} %.\n")
print("Classification Report:\n", cr)

ensemble_clf.append(model_pipeline)
acc_clf['knn'] = accuracy
report_clf['knn'] = classification_report(y_test, y_pred, output_dict=True)

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Innocent', 'Suspect'], yticklabels=['Innocent', 'Suspect'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ROC Curve
y_prob = model_pipeline.predict_proba(X_test)[:, 1]  # Probabilities for the positive class
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
roc_area['knn'] = roc_auc
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)

plt.figure()
plt.plot(recall, precision, color='blue', lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.show()

"""## Decision Tree (DT)"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
import matplotlib.pyplot as plt

# Create a pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', DecisionTreeClassifier(random_state=42))
])
# Train the model
model_pipeline.fit(X_train, y_train)

# Predict on the test set
y_pred = model_pipeline.predict(X_test)

# Evaluate the model
accuracy = 100 * accuracy_score(y_test, y_pred)
cr = classification_report(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f} %.\n")
print("Classification Report:\n", cr)

ensemble_clf.append(model_pipeline)
acc_clf['dt'] = accuracy
report_clf['dt'] = classification_report(y_test, y_pred, output_dict=True)

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Innocent', 'Suspect'], yticklabels=['Innocent', 'Suspect'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ROC Curve
y_prob = model_pipeline.predict_proba(X_test)[:, 1]  # Probabilities for the positive class
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
roc_area['dt'] = roc_auc
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)

plt.figure()
plt.plot(recall, precision, color='blue', lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.show()

"""# Part D:- Building a Custom Ensemble Model: Combining Hand-Coded Naive Bayes with Sklearn Classifiers for Enhanced Performance"""

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder

class VotingEnsemble(BaseEstimator, ClassifierMixin):
    def __init__(self, pipelines):
        self.pipelines = pipelines
        print(self.pipelines)
        self.label_encoder = LabelEncoder()

    def fit(self, X, y):
        # Fit the label encoder for consistency in label handling
        self.label_encoder.fit(y)
        return self

    def predict(self, X):
        # Get predictions from each pipeline
        predictions = np.array([pipeline.predict(X) for pipeline in self.pipelines])
        # Apply majority voting
        return self._majority_voting(predictions)

    def predict_proba(self, X):
        # Get probabilities from each pipeline
        probabilities = np.array([pipeline.predict_proba(X) for pipeline in self.pipelines])
        # Average the probabilities
        return np.mean(probabilities, axis=0)

    def _majority_voting(self, predictions):
        # Transpose predictions to get votes for each instance
        votes = predictions.T
        # Majority voting: mode of the votes
        return np.array([np.bincount(vote).argmax() for vote in votes])

ensemble_model = VotingEnsemble(pipelines=ensemble_clf)
# ensemble_model.fit(X_train, y_train)

# Predict on the test set
y_pred = ensemble_model.predict(X_test)

# Evaluate the model
accuracy = 100 * accuracy_score(y_test, y_pred)
cr = classification_report(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f} %.\n")
print("Classification Report:\n", cr)

acc_clf['en'] = accuracy
report_clf['en'] = classification_report(y_test, y_pred, output_dict=True)

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Innocent', 'Suspect'], yticklabels=['Innocent', 'Suspect'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ROC Curve
y_prob = model_pipeline.predict_proba(X_test)[:, 1]  # Probabilities for the positive class
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
roc_area['en'] = roc_auc
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)

plt.figure()
plt.plot(recall, precision, color='blue', lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.show()

"""# Performance Comparison of Individual Classifiers and Ensemble Model"""

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC Area']
classifiers = ['nb_m', 'nb', 'svc', 'knn', 'dt', 'en']
def construct_table(label):
    return pd.DataFrame({
        'Precision': {clf: report_clf[clf][label]['precision'] for clf in classifiers},
        'Recall': {clf: report_clf[clf][label]['recall'] for clf in classifiers},
        'F1-Score': {clf: report_clf[clf][label]['f1-score'] for clf in classifiers},
    }).T

df_acc=pd.DataFrame({'Accuracy': acc_clf}).T
df_roc=pd.DataFrame({'ROC Area': roc_area}).T
df_0=construct_table('0')
df_1=construct_table('1')
fig, axs = plt.subplots(1, 2, figsize=(20, 6))

# Accuracy plot
sns.lineplot(x=df_acc.columns, y=df_acc.loc['Accuracy'], marker='o', linewidth=2.5, markersize=10, ax=axs[0])
axs[0].set_title('Accuracy Comparison', fontsize=16, weight='bold')
axs[0].set_ylabel('Accuracy (%)', fontsize=14)
axs[0].set_xlabel('Classifiers', fontsize=14)
axs[0].grid(True, linestyle='--', alpha=0.5)

# Mark the best accuracy
best_acc_clf = max(acc_clf, key=acc_clf.get)
best_acc_value = acc_clf[best_acc_clf]
axs[0].scatter(best_acc_clf, best_acc_value, color='red', s=100, zorder=5, edgecolor='black')
axs[0].annotate(f'Best: {best_acc_clf}', xy=(best_acc_clf, best_acc_value), xytext=(best_acc_clf, best_acc_value + 1.05),
                 arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=12, ha='center')

# Draw perpendicular lines
axs[0].axhline(y=best_acc_value, color='grey', linestyle='--', xmin=0, xmax=1, zorder=4)
axs[0].axvline(x=best_acc_clf, color='grey', linestyle='--', ymin=0, ymax=1, zorder=4)

# ROC Area plot
sns.lineplot(x=df_roc.columns, y=df_roc.loc['ROC Area'], marker='o', linewidth=2.5, markersize=10, ax=axs[1])
axs[1].set_title('ROC Area Comparison', fontsize=16, weight='bold')
axs[1].set_ylabel('ROC Area', fontsize=14)
axs[1].set_xlabel('Classifiers', fontsize=14)
axs[1].grid(True, linestyle='--', alpha=0.5)

# Mark the best ROC Area
best_roc_clf = max(roc_area, key=roc_area.get)
best_roc_value = roc_area[best_roc_clf]
axs[1].scatter(best_roc_clf, best_roc_value, color='red', s=100, zorder=5, edgecolor='black')
axs[1].annotate(f'Best: {best_roc_clf}', xy=(best_roc_clf, best_roc_value), xytext=(best_roc_clf, best_roc_value + 0.02),
                 arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=12, ha='center')

# Draw perpendicular lines
axs[1].axhline(y=best_roc_value, color='grey', linestyle='--', xmin=0, xmax=1, zorder=4)
axs[1].axvline(x=best_roc_clf, color='grey', linestyle='--', ymin=0, ymax=1, zorder=4)

# Add legends
legend_labels = {
    'nb_m': 'Naive Bayes (Implementation)',
    'nb': 'Naive Bayes',
    'svc': 'Support Vector Classifier',
    'knn': 'K-Nearest Neighbors',
    'dt': 'Decision Tree',
    'en': 'Ensemble Methods'
}
handles = [plt.Line2D([0], [0], color='black', marker='o', markersize=10, linestyle='-', label=f'{k}: {v}') for k, v in legend_labels.items()]

# Add legend to the second subplot (ROC Area)
axs[1].legend(handles=handles, title='Classifiers', title_fontsize='13', loc='upper left', bbox_to_anchor=(1, 1))

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plot
plt.show()

fig, axs = plt.subplots(1, 3, figsize=(18, 6))

# Define colors
colors = {'0': 'blue', '1': 'orange'}

# Plot Precision
sns.lineplot(x=df_0.columns, y=df_0.loc['Precision'], marker='o', linewidth=2.5, markersize=10, label='0', ax=axs[0], color=colors['0'])
sns.lineplot(x=df_1.columns, y=df_1.loc['Precision'], marker='o', linewidth=2.5, markersize=10, label='1', ax=axs[0], color=colors['1'])
axs[0].set_title('Precision Comparison', fontsize=16, weight='bold')
axs[0].set_ylabel('Score', fontsize=12)
axs[0].set_xlabel('Classifiers', fontsize=12)
axs[0].legend(title='DataFrames', title_fontsize='13', loc='best')
axs[0].grid(True, linestyle='--', alpha=0.5)

# Plot Recall
sns.lineplot(x=df_0.columns, y=df_0.loc['Recall'], marker='o', linewidth=2.5, markersize=10, label='0', ax=axs[1], color=colors['0'])
sns.lineplot(x=df_1.columns, y=df_1.loc['Recall'], marker='o', linewidth=2.5, markersize=10, label='1', ax=axs[1], color=colors['1'])
axs[1].set_title('Recall Comparison', fontsize=16, weight='bold')
axs[1].set_ylabel('Score', fontsize=12)
axs[1].set_xlabel('Classifiers', fontsize=12)
axs[1].legend(title='DataFrames', title_fontsize='13', loc='best')
axs[1].grid(True, linestyle='--', alpha=0.5)

# Plot F1-Score
sns.lineplot(x=df_0.columns, y=df_0.loc['F1-Score'], marker='o', linewidth=2.5, markersize=10, label='0', ax=axs[2], color=colors['0'])
sns.lineplot(x=df_1.columns, y=df_1.loc['F1-Score'], marker='o', linewidth=2.5, markersize=10, label='1', ax=axs[2], color=colors['1'])
axs[2].set_title('F1-Score Comparison', fontsize=16, weight='bold')
axs[2].set_ylabel('Score', fontsize=12)
axs[2].set_xlabel('Classifiers', fontsize=12)
axs[2].legend(title='DataFrames', title_fontsize='13', loc='best')
axs[2].grid(True, linestyle='--', alpha=0.5)

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plot
plt.show()