from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import tag_selection_form, model_name_selection_form, upload_file_form, topic_extraction_form
from .models import Classification_Documents
import boto3, botocore
from botocore.config import Config
import time, os, sys
from tempfile import NamedTemporaryFile
from smart_open import open
from collections import defaultdict
from io import StringIO
import numpy as np
import pandas as pd
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.test.utils import datapath
from gensim import models
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm as tqdm
from pprint import pprint
import json



