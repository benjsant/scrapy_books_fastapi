class CleanPipeline:
    """Nettoyage et type conversion des items"""
    def process_item(self, item, spider):
        # Convert price to float (déjà fait dans spider si voulu)
        if isinstance(item.get("price_excl_tax"), str):
            item["price_excl_tax"] = float(item["price_excl_tax"].replace("£", ""))
        if isinstance(item.get("price_incl_tax"), str):
            item["price_incl_tax"] = float(item["price_incl_tax"].replace("£", ""))
        if isinstance(item.get("tax"), str):
            item["tax"] = float(item["tax"].replace("£", ""))
        
        # Nettoyer description
        if item.get("description"):
            item["description"] = " ".join(item["description"].strip().split())
        return item
