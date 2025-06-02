# pipelines.py

class ApolloPipeline:
    def process_item(self, item, spider):
        """
        Processes each scraped item.
        You can add more complex cleaning, validation, or database storage logic here.
        """
        # Example: Ensure essential fields are not empty
        if not item.get('name') and not item.get('email'):
            spider.logger.warning(f"Skipping item with missing name and email: {item}")
            raise DropItem("Missing essential data")

        # Example: Convert to proper types if necessary (e.g., numbers)
        # try:
        #     item['employees'] = int(item['employees'])
        # except (ValueError, TypeError):
        #     item['employees'] = None

        # You would typically save to a database here
        # self.database_connection.insert(item)

        return item
