def config(config_file = "pagerank.settings"):
    """
    An example of *.settings
    {
        "accuracy": 0.9
    }
    

    """
    import numpy as np
    import os
    accuracy = np.linspace(0.5, 1.0, 20)
    for acc in accuracy:
        print("Accuracy: ", acc)
        with open(config_file, "w") as f:
            import json
            json.dump({"accuracy": acc}, f)
        # run the pagerank program 
        os.system(f"python tuner.py pagerank --stop-after=30")

if __name__ == "__main__":
    config()