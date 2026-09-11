"""
Recommendation Engine for NepCart.
Implements Item-to-Item Collaborative Filtering using Jaccard Similarity.
"""

from collections import defaultdict
from product.models import Product
from cart.models import CartItem


def get_jaccard_recommendations(target_product, limit=4):
    """
    Computes Item-to-Item Collaborative Filtering recommendations using the Jaccard Similarity Coefficient:
    
        Jaccard(A, B) = |Users(A) ∩ Users(B)| / |Users(A) ∪ Users(B)|
    
    1. Identifies all users/sessions who interacted with (ordered or carted) target_product A.
    2. Finds all candidate products B that shared at least one customer/session with A.
    3. Calculates the Jaccard similarity between target_product A and candidate B.
    4. Ranks candidate products by Jaccard similarity descending.
    5. Fallback: If co-occurrence data is sparse (e.g. cold start), backfills recommendations
       with top available products in the same category or overall store.
    """
    if not target_product:
        return []

    # Identify user identifiers (user_id if authenticated, otherwise cart_id/session) for target product
    target_interactions = CartItem.objects.filter(product=target_product)
    
    users_target = set()
    for item in target_interactions:
        if item.user_id:
            users_target.add(f"u_{item.user_id}")
        elif item.cart_id:
            users_target.add(f"c_{item.cart_id}")

    similarities = {}

    # If target product has interaction history, find candidate co-occurrences
    if users_target:
        # Find all other cart items associated with these users/sessions
        co_items = CartItem.objects.filter(
            product__is_available=True
        ).exclude(product=target_product)

        # Map candidate product_id -> set of user/session identifiers
        product_users = defaultdict(set)
        for item in co_items:
            key = f"u_{item.user_id}" if item.user_id else f"c_{item.cart_id}"
            if key:
                product_users[item.product_id].add(key)

        # Compute Jaccard Similarity for each candidate product
        for prod_id, users_candidate in product_users.items():
            intersection = len(users_target.intersection(users_candidate))
            if intersection > 0:
                union = len(users_target.union(users_candidate))
                score = intersection / union if union > 0 else 0
                similarities[prod_id] = score

    # Sort products by Jaccard score descending
    ranked_product_ids = sorted(similarities, key=similarities.get, reverse=True)
    recommended_products = list(Product.objects.filter(id__in=ranked_product_ids, is_available=True))
    
    # Preserve score ordering
    id_to_score = {pid: similarities.get(pid, 0) for pid in ranked_product_ids}
    recommended_products.sort(key=lambda p: id_to_score.get(p.id, 0), reverse=True)
    recommended_products = recommended_products[:limit]

    # Fallback (Cold-Start Strategy): If fewer than limit recommendations found,
    # fill with available products from the same category
    if len(recommended_products) < limit:
        needed = limit - len(recommended_products)
        existing_ids = {p.id for p in recommended_products} | {target_product.id}
        category_fallback = list(
            Product.objects.filter(
                catogery=target_product.catogery,
                is_available=True
            ).exclude(id__in=existing_ids)[:needed]
        )
        recommended_products.extend(category_fallback)

    # Secondary Fallback: If category has no more products, fill with popular/store products
    if len(recommended_products) < limit:
        needed = limit - len(recommended_products)
        existing_ids = {p.id for p in recommended_products} | {target_product.id}
        general_fallback = list(
            Product.objects.filter(
                is_available=True
            ).exclude(id__in=existing_ids)[:needed]
        )
        recommended_products.extend(general_fallback)

    return recommended_products[:limit]
