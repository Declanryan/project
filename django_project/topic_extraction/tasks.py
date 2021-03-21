from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .forms import upload_file_form, topic_extraction_form
from .models import Topic_extraction_Documents
import boto3
from botocore.config import Config
import time, os, sys
import pandas as pd
import stanza
from io import StringIO
import numpy as np
import pandas as pd
import gensim
import gensim.corpora as corpora
from gensim.test.utils import datapath
from gensim import models
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm as tqdm
from pprint import pprint
import json
from django.contrib import messages
from django.conf import settings

@shared_task(bind=True)
def topic_test_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for i in range(seconds):
        time.sleep(1)
        result += i
        progress_recorder.set_progress(i + 1, seconds)
    return result





@shared_task(bind=True)
def extract_topics(self, pk, topics):
	progress_recorder = ProgressRecorder(self) 
	doc = Topic_extraction_Documents.objects.get(pk=pk)# get the document ref from the database
	documentName = str(doc.document)# get the real name of the doc

	aws_id = settings.AWS_ACCESS_KEY_ID# AWS ACCESS
	aws_secret = settings.AWS_SECRET_ACCESS_KEY
	REGION = 'eu-west-1'

	client = boto3.client('s3', region_name = REGION, aws_access_key_id=aws_id,
	        aws_secret_access_key=aws_secret)

	bucket_name = settings.AWS_STORAGE_BUCKET_NAME

	object_key = documentName
	csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
	body = csv_obj['Body']
	csv_string = body.read().decode('utf-8')

	data = pd.read_csv(StringIO(csv_string)) #CREATE DATAFRAME FROM CSV

	documents = data['content'] # assign docs to content
	#print(documents)# testing

	nlp = spacy.load("en_core_web_md") # load spacy model for token and lemma

	# My list of stop words.
	stop_list = ["â€", "â€","™", "Mrs.","Ms.","say","'s","Mr.","0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about", "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad", "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again", "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk", "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c", "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd", "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm", "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt", "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy", "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite", "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn", "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due", "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei", "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end", "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc", "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows", "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu", "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give", "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings", "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt", "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes", "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how", "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il", "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead", "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd", "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt", "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l", "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les", "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll", "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more", "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly", "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new", "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt", "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh", "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo", "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3", "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe", "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po", "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu", "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc", "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively", "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc", "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall", "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't", "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly", "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss", "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb", "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll", "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru", "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward", "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve", "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd", "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w", "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well", "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever", "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim", "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose", "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won", "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet", "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves", "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz",]

	# Updates spaCy's default stop words list with my additional words. 
	nlp.Defaults.stop_words.update(stop_list)

	# Iterates over the words in the stop words list and resets the "is_stop" flag.
	for word in STOP_WORDS:
	    lexeme = nlp.vocab[word]
	    lexeme.is_stop = True

	def lemmatizer(doc):
	    # This takes in a doc of tokens from the NER and lemmatizes them. 
	    # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
	    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
	    doc = u' '.join(doc)
	    return nlp.make_doc(doc)
	    
	def remove_stopwords(doc):
	    # This will remove stopwords and punctuation.
	    # Use token.text to return strings, which we'll need for Gensim.
	    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
	    return doc

	# Add to the default pipeline.
	nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
	nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

	doc_list = []
	# Iterates through each article in the corpus.
	count =0
	for doc in tqdm(documents):
	    # Passes that article through the pipeline and adds to a new list.
	    pr = nlp(doc)
	    #print(pr) # testing
	    doc_list.append(pr)
	    progress_recorder.set_progress(count +1, len(documents)) # update progress
	    count +=1 # update count
	# Creates, which is a mapping of word IDs to words.
	words = corpora.Dictionary(doc_list)

	# Turns each document into a bag of words.
	corpus = [words.doc2bow(doc) for doc in doc_list]
	
	lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
	                                           id2word=words,
	                                           num_topics=topics, 
	                                           random_state=2,
	                                           update_every=1,
	                                           chunksize=50,
	                                           passes=10,
	                                           alpha='auto')

	#################### save the model ########################
	#gensim_lda_model = datapath("saved_models/classification_model")
	#lda_model.save('saved_models/classification_model/gensim_lda_model.gensim')
	############################################################

	# compare a docs results and find the higest probability
	def topic_prediction(my_document):
	    x = nlp(my_document)
	    other_corpus = words.doc2bow(x) # convert to bow
	    output = list(lda_model[other_corpus])
	    # print(output) # testing
	    topics = sorted(output,key=lambda x:x[1],reverse=True)
	    return topics[0][0]

	# loop through documents and get the result with the highest probability
	topic_result = []
	for doc in documents:
	    topic_result.append(topic_prediction(doc))

	# print(topic_result) # testing

	# words occuring in that topic and its relative weight
	topics_list = []
	for idx, topic in lda_model.print_topics(-1):
	    topics_list.append("Topic: {} Words: {}".format(idx, topic))
	    
	# finds the total docs for each topic
	topic_totals = []
	for i in range(topics):
	    topic_totals.append(topic_result.count(i))
	# print(topic_totals) #testing

	# Compute Perplexity
	perplexity_score = ('\nPerplexity score: ', lda_model.log_perplexity(corpus))  # a measure of how good the model is. lower the better.
	# Compute Coherence Score
	#coherence_model_lda = CoherenceModel(model=lda_model, texts=corpus, dictionary=words, coherence='c_v')
	#coherence_lda = coherence_model_lda.get_coherence()
	#print('\nCoherence Score: ', coherence_lda)

	topics_dict = {} 
	  
	# Adding list as value 
	topics_dict["Topic_result"] = topic_result 
	topics_dict["Topics_list"] = topics_list
	topics_dict["Topic_totals"] = topic_totals
	topics_dict["Perplexity_score"] = perplexity_score

	return topics_dict
	