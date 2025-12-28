"""
Download Pre-trained Models for Ticket Classifier
One-time setup (~5-10 minutes)
"""

print("=" * 80)
print("DOWNLOADING MODELS FOR TICKET CLASSIFIER")
print("=" * 80)
print("\nThis will download ~350MB of models (Flair NER).")
print("Sentence-transformers model is already cached from FAISS.\n")
print("Estimated time: 5-10 minutes\n")
print("=" * 80 + "\n")

try:
    # Download Flair NER model
    print("Downloading Flair NER model (ner-english-large)...")
    print("Size: ~350MB\n")

    from flair.models import SequenceTagger

    tagger = SequenceTagger.load('ner-english-large')
    print("\n[SUCCESS] Flair NER model downloaded successfully!")

    # Test it
    from flair.data import Sentence
    test_sentence = Sentence("I want to recharge 500 rupees")
    tagger.predict(test_sentence)
    print("[SUCCESS] Model test successful!")

    print("\n" + "=" * 80)
    print("ALL MODELS READY!")
    print("=" * 80)
    print("\nYou can now run your app:")
    print("  streamlit run app.py")
    print("  or")
    print("  python main.py")
    print("\n" + "=" * 80 + "\n")

except KeyboardInterrupt:
    print("\n\n[WARNING] Download interrupted by user")
    exit(1)

except Exception as e:
    print(f"\n\n[ERROR] {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Check your internet connection")
    print("  2. Ensure you have ~500MB free disk space")
    print("  3. Try running: pip install --upgrade flair")
    exit(1)
