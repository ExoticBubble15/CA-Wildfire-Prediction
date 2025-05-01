import subprocess
import sys
import os
import shutil

if __name__ == "__main__":
	try:
		folder = "GENERATED_EXAMPLES/"
		if os.path.exists(folder):
			shutil.rmtree(folder)
		os.makedirs(folder)
		print("folder GENERATED_EXAMPLES cleared\n")

		subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

		image1 = "python3 graph-city-attributes.py Thermalito default avgPress"
		print(f"generating image 1 from README.md\nexecuting: {image1}\n")
		subprocess.run(image1, shell=True, check=True)

		image2 = "python3 graph-city-attributes.py \"San Luis Obispo\" default totalSatGHI"
		print(f"generating image 2 from README.md\nexecuting: {image2}\n")
		subprocess.run(image2, shell=True, check=True)

		image3 = "python3 graph-city-attributes.py \"Mammoth Lakes\" default avgDBT avgWSpd"
		print(f"generating image 3 from README.md\nexecuting: {image3}\n")
		subprocess.run(image3, shell=True, check=True)

		image4 = "python3 graph-all-cities-attributes.py avgDBT totalSatGHI avgPress"
		print(f"generating image 4 from README.md\nexecuting: {image4}\n")
		subprocess.run(image4, shell=True, check=True)

		image5 = "python3 graph-all-cities-attributes.py avgVisib avgCeil"
		print(f"generating image 5 from README.md\nexecuting: {image5}\n")
		subprocess.run(image5, shell=True, check=True)

		engineerFeatures = f"python3 feature-engineering.py {folder}"
		print(f"ENGINEERING FEATURES\nexecuting: {engineerFeatures}")
		subprocess.run(engineerFeatures, shell=True, check=True)
		print(f"check `{folder}engineered-training.csv`, `{folder}engineered-validation.csv`, and `{folder}engineered-testing.csv` for results\n")

		example1 = f"python3 knn.py validation {folder}example1_validation_subset 2021-06-13 2021-06-18"
		print(f"MODEL EXAMPLE 1\nexecuting: {example1}")
		subprocess.run(example1, shell=True, check=True)
		print(f"check `{folder}example1_validation_subset.txt` for results\n")

		example2 = f"python3 knn.py testing {folder}example2_testing_subset 2024-08-20 2024-08-29"
		print(f"MODEL EXAMPLE 2\nexecuting: {example2}")
		subprocess.run(example2, shell=True, check=True)
		print(f"check `{folder}example2_testing_subset.txt` for results\n")

		print(f"look at the `{folder}` folder to see all generated examples\n")
		print("thank you for checking out my project :D happy summer! ඩාඩාඩා")
	except:
		print("something went wrong (you really shouldnt be seeing this...)")