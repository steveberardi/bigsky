import csv

bayer = {}
flamsteed = {}

with open("build/bigsky.stars.csv", "r") as starfile:
    reader = csv.DictReader(starfile)
    for row in reader:
        hip_id = row["hip_id"]
        
        if not hip_id:
            continue

        hip_id = int(hip_id)

        if row["bayer"]:
            bayer[hip_id] = row["bayer"]
        
        if row["flamsteed"]:
            flamsteed[hip_id] = int(row["flamsteed"])

print(bayer)
print(flamsteed)
