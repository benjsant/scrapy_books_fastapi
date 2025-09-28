import csv

class CSVPipeline:
    def __init__(self):
        self.file = open("data/books_data.csv", "w", newline="", encoding="utf-8")
        self.writer = None
        self.seen_upcs = set()

    def process_item(self, item, spider):
        if item["upc"] in self.seen_upcs:
            return item
        self.seen_upcs.add(item["upc"])

        if self.writer is None:
            keys = item.keys()
            self.writer = csv.DictWriter(self.file, fieldnames=keys)
            self.writer.writeheader()
        self.writer.writerow(item)
        return item

    def close_spider(self, spider):
        self.file.close()
