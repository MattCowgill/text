#note: I think layer 0 is the input embedding. 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import torch
from transformers import AutoConfig, AutoModel, AutoTokenizer
import numpy as np

import nltk
try:
    nltk.data.find('tokenizers/punkt/PY3/english.pickle')
except:
    nltk.download("punkt")

from nltk.tokenize import sent_tokenize

#TODO:#dictionary of pretrained weights to models
def hgTransformerGetEmbedding(text_strings,
                              model = 'bert-base-uncased',
                              layers = 'all',  
                              return_tokens = True):
    """
    Summary line.

    Parameters
    ----------
    text_strings : list
        list of strings, each is embedded separately
    model : str
        shortcut name for Hugging Face pretained model
        Full list https://huggingface.co/transformers/pretrained_models.html
    layers : str or list
        'all' or an integer list of layers to keep
    return_tokens : boolean
        return tokenized version of text_strings


    Returns
    -------
    all_embs : list
        embeddings for each item in text_strings
    all_toks : list, optional
        tokenized version of text_strings

    """

    config = AutoConfig.from_pretrained(model, output_hidden_states=True)
    tokenizer = AutoTokenizer.from_pretrained(model)
    transformer_model = AutoModel.from_pretrained(model, config=config)
    
    maxTokensPerSeg = tokenizer.max_len_sentences_pair//2

    ##Check and Adjust Input Typs
    if not isinstance(text_strings, list):
        text_strings = [text_strings]
    if layers != 'all':
        if not isinstance(layers, list):
            layers = [layers]
        layers = [int(i) for i in layers]

    all_embs = []
    all_toks = []

    for text_string in text_strings:

        input_ids = tokenizer.encode(text_string, add_special_tokens=True)
        if return_tokens:
            tokens = tokenizer.convert_ids_to_tokens(input_ids)
        
        # if number of tokens greater than the model can handle
        # embedd each sentence separately
        if len(input_ids) > maxTokensPerSeg:
            this_embs, this_toks = [], []
            for sent_str in sent_tokenize(text_string):
                input_ids = tokenizer.encode(sent_str, add_special_tokens=True)
                if return_tokens:
                    tokens = tokenizer.convert_ids_to_tokens(input_ids)
                
                with torch.no_grad():
                    hidden_states = transformer_model(torch.tensor([input_ids]))[2]
                    if layers != 'all': 
                        hidden_states = [hidden_states[l] for l in layers]
                    hidden_states = [h.tolist() for h in hidden_states]
                    this_embs.extend(hidden_states)
                    if return_tokens:
                        this_toks.extend(tokens)
            all_embs.append(this_embs)
            all_toks.append(this_toks)

        else:
            with torch.no_grad():
                hidden_states = transformer_model(torch.tensor([input_ids]))[2]
                if layers != 'all': 
                    hidden_states = [hidden_states[l] for l in layers]
                hidden_states = [h.tolist() for h in hidden_states]
                all_embs.append(hidden_states)
                if return_tokens:
                    all_toks.append(tokens)

    if return_tokens:
        return all_embs, all_toks
    else:
        return all_embs

	
#EXAMPLE TEST CODE:
#if __name__   == '__main__':
#    embeddings, tokens = hgTransformerGetEmbedding("Here is one sentence.", layers=[0,10])
#    print(np.array(embeddings).shape)
#    print(tokens)
#
#    embeddings, tokens = hgTransformerGetEmbedding("Here is more sentences. But why is not . and , and ? indicated with SEP?", layers=[0,10])
#    print(np.array(embeddings).shape)
#    print(tokens)

