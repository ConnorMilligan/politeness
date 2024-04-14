import sys
import time
import os

from convokit import Corpus
from convokit import download
from convokit import TextParser
from convokit import PolitenessStrategies

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
    score = sum([utt.meta["politeness_strategies"].get(politeness_feature, 0) * weight for politeness_feature, weight in politeness_features.items()])
    
    max_score = sum(abs(weight) for weight in politeness_features.values())
    min_score = -max_score
    
    normalized_score = 2 * (score - min_score) / (max_score - min_score) - 1
    return normalized_score

def main():
    # check that there is 1 argument
    if len(sys.argv) != 2:
        print("Please specify a corpus name.")
        sys.exit(1)

    corpus_name = sys.argv[1]

    # make sure corpus is available
    if corpus_name not in supported_corpora:
        print("Corpus not supported.")
        sys.exit(1)

    start_time = time.time()

    print("Loading corpus...")
    corpus = Corpus(filename=download(corpus_name))#, utterance_end_index=5000)

    print("Transforming corpus...")
    parser = TextParser(verbosity=1000)
    corpus = parser.transform(corpus)

    ps = PolitenessStrategies()

    print("Extracting politeness strategies...")
    corpus = ps.transform(corpus, markers=True)

    # create data folder if it doesn't exist
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)

    # grab politeness scores for each utterance and write them to a file
    df = ps.summarize(corpus, plot=True)
    df.to_csv(dataFolder + corpus_name + "-dataframe.csv")

    # isolate the 5 most polite and 5 most negative utterances
    most_polite = {}
    most_negative = {}

    with open(dataFolder + corpus_name + "-politeness_scores.csv", "w", encoding='utf-8') as f:
        for utt in corpus.iter_utterances():
            f.write(f"{utt.id},{get_politeness_score(utt):.2f}\n")
            curr_score = get_politeness_score(utt)

            # add to most polite dictionary if it is more polite than the least polite utterance in the dictionary
            # remove the least polite utterance from the dictionary & sort the dictionary by politeness score
            # the politeness score is the key in the dictionary and the text of the utterance is the value
            if len(most_polite) < 5 or curr_score > list(most_polite.keys())[0]:
                most_polite[curr_score] = utt.text
                most_polite = dict(sorted(most_polite.items()))

                if len(most_polite) > 5:
                    most_polite.pop(list(most_polite.keys())[0])

            # repeat the same process for the most negative utterances
            if len(most_negative) < 5 or curr_score < list(most_negative.keys())[0]:
                most_negative[curr_score] = utt.text
                most_negative = dict(sorted(most_negative.items()))

                if len(most_negative) > 5:
                    most_negative.pop(list(most_negative.keys())[0])




    print(f"Most polite utterance: {most_polite[max(most_polite.keys())]}")
    print(f"Politeness score: {max(most_polite.keys())}")
    print()
    print(f"Most negative utterance: {most_negative[min(most_negative.keys())]}")
    print(f"Politeness score: {min(most_negative.keys())}")

    end_time = time.time()

    # Write the negative and positive utterances to a single file in the same format as above
    with open(dataFolder + corpus_name + "-negative_positive_utterances.txt", "w", encoding='utf-8') as f:
        for score, text in most_negative.items():
            f.write(f"Negative, {score:.2f}:\n {text}\n")
        f.write("\n")
        for score, text in most_polite.items():
            f.write(f"Positive, {score:.2f}:\n {text}\n")
        f.write(f"\n\nTotal execution time: {end_time - start_time:.2f} seconds\n")

    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()