# ChemTextMining
## Short description of repository
##### This repository contains code and additional resources for experimenting on disease entities extraction using conditional random fields. Structure is as follows:<br>
0. webmd_corpus.json is a full corpus. 
1. classification_pipe.py - entry point of program. 
2. vocabularies - directory with used vocabularies in txt format, each line contains one vocabulary entity.
3. clustered words - directory with words clustered using brown clustering algorithm.
4. corpus_json - directory with datasets used in experiments.
5. word2vec - directory with word embeddings
6. remaining is utility code

## Usage:
1. Install all the requirements.
            
            pip install -r requirements.txt
   Also perl is need to be installed         
            
2. Specify in "features" dictionary current token features from list of available features. Also it's necessary to define context size by setting k_prev(tokens to look before) and k_next(tokens to look forward) and features for each context token(in prev_features and next_features).
3. Run code:

          python classificaton_pipe.py
          
4. Output is in format:
        
        ...
        Average exact score:
          precision	recall	fscore
        
        Average weak score:
          precision	recall	fscore
          
   
#### Note: To use different word embedding vectors need to specify it in crf/features.py in load_w2v_model function.
#### Citing: 
Please cite this paper: http://www.dialog-21.ru/media/3932/miftahutdinovzshetal.pdf
