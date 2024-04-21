import pprint
from convokit import Corpus
from convokit import download
from convokit import TextParser
from convokit import PolitenessStrategies

import json

# Reminder to call: python3 -m spacy download en_core_web_sm before running this script

# politeness features and weights
politeness_features = {
    "feature_politeness_==Gratitude==": 0.87,
    "feature_politeness_==Deference==": 0.78,
    "feature_politeness_==Indirect_(greeting)==": 0.43,
    "feature_politeness_==HASPOSITIVE==": 0.12,    
    "feature_politeness_==HASNEGATIVE==": -0.13,

    "feature_politeness_==Apologizing==": 0.36,

    "feature_politeness_==Please==": 0.49,
    "feature_politeness_==Please_start==": -0.30,

    "feature_politeness_==Indirect_(btw)==": 0.63,
    "feature_politeness_==Direct_question==": -0.27,
    "feature_politeness_==Direct_start==": -0.43,

    "feature_politeness_==SUBJUNCTIVE==": 0.47,
    "feature_politeness_==INDICATIVE==": 0.09,

    "feature_politeness_==1st_person_start==": 0.12,
    "feature_politeness_==1st_person==": 0.08,
    "feature_politeness_==2nd_person==": 0.05,
    "feature_politeness_==2nd_person_start==": -0.30,

    "feature_politeness_==Hedges==": 0.14,
    "feature_politeness_==Factuality==": -0.38,
}

supported_corpora = ["wiki-corpus", "reddit-corpus-small", "conversations-gone-awry-cmv-corpus", "conversations-gone-awry-corpus"]
dataFolder = "data/"

def get_politeness_score(utt):
    # Take each politeness feature and multiply it by its weight, then sum all the values
    score = sum([utt.meta["politeness_strategies"].get(politeness_feature, 0) * weight for politeness_feature, weight in politeness_features.items()])
    
    # Sum of absolute weights
    abs_weights_sum = sum(abs(weight) for weight in politeness_features.values())
    
    # Scale the score based on the sum of absolute weights
    # Avoid division by zero
    if abs_weights_sum == 0:
        normalized_score = 0
    else:
        normalized_score = score / abs_weights_sum
    
    return normalized_score

def main():
    print("Loading corpus...")
    corpus = Corpus(filename=download("wiki-corpus"), utterance_end_index=100)

    print("Transforming corpus...")
    parser = TextParser(verbosity=1000)
    corpus = parser.transform(corpus)

    ps = PolitenessStrategies()

    print("Extracting politeness strategies...")
    corpus = ps.transform(corpus, markers=True)

    # fetch first utterance
    # 10 good too 12
    utt = list(corpus.iter_utterances())[20]
    print(utt.id+"\n")

    # print out metadata
    print(utt)
    print()

    # loop through dictionary and print out key value pairs recursively
    for key in utt.meta:
        if isinstance(utt.meta[key], dict):
            if isinstance(utt.meta[key], dict):
                print(key + ":")
                pprint.pprint(utt.meta[key])
            else:
                print(key + ":")
                pprint.pprint(utt.meta[key])
        else:
            print(key + ": " + str(utt.meta[key]))
    

    print("\n" + utt.text + "\n")

    # print politeness markers greater than 0
    print("Politeness markers:")
    for key in utt.meta["politeness_strategies"]:
        if utt.meta["politeness_strategies"][key] > 0:
            print(f"{key}: {utt.meta['politeness_strategies'][key]} - ({politeness_features[key]})")


    form = ""
    total = 0
    for key in utt.meta["politeness_strategies"]:
        if utt.meta["politeness_strategies"][key] > 0:
            form += f"({utt.meta['politeness_strategies'][key]}x({politeness_features[key]})) + "
            total += utt.meta["politeness_strategies"][key] * politeness_features[key]
    
    total = round(total, 2)
    abs_weight = sum(abs(weight) for weight in politeness_features.values())
    print(f"\nScore = {form[:-3]} = {total}")
    print(f"|abs weights| = {abs_weight}")
    print(f"Normalized Score = {total}/|abs weights| = {total/abs_weight}\n")

    # get politeness score
    score = get_politeness_score(utt)
    print(f"Politeness score: {score}")

if __name__ == "__main__":
    main()