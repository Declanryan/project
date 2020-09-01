from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import Sentiment_form

def predict(filename):
	#load and prepare data

	#load model
	best_model = SentimentAnalysisModel(vocab_size+1, max_seqlen)
	best_model.build(input_shape=(batch_size, max_seqlen))
	best_model.load_weights(best_model_file)
	best_model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

	# predict on batches
	predictions = []
	idx2word[0] = "PAD"
	is_first_batch = True
	for test_batch in test_dataset:
	    inputs_b = test_batch
	    pred_batch = best_model.predict(inputs_b)
	    predictions.extend([(1 if p > 0.5 else 0) for p in pred_batch])
	    labels.extend([l for l in labels_b])
	    if is_first_batch:
	        for rid in range(inputs_b.shape[0]):
	            words = [idx2word[idx] for idx in inputs_b[rid].numpy()]
	            words = [w for w in words if w != "PAD"]
	            sentence = " ".join(words)
	            print("{:d}\t{:d}\t{:s}".format(labels[rid], predictions[rid], sentence))
	        is_first_batch = False
	return(predictions)

#@login_required
def sentiment_check(request):
	 if request.method == 'POST':
    form = Sentiment_form(request.POST)
    if form.is_valid():
        form.save()
        text= form.cleaned_data.get('text')




        
        messages.success(request, f'Account created for {username}!')
        return redirect('users/login.html')
else:
    form = UserRegisterForm()
return render(request, 'users/register.html', {'form': form})