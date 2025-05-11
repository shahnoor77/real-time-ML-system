def get_model_name(product_id: str) -> str:
    """
    Get the model name from given product_id.
    Args:
        product_id (str): The product ID.
    Returns:
        str: The model name.
    """    
    return f'{product_id.replace("/", "_")}_price_change_predictor'