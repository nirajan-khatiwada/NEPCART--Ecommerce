# RECOMMENDATION ALGORITHM IN NEPCART

This document provides a concise and practical explanation of the **Recommendation Algorithm** implemented in **NepCart**.

---

## 1. What is It?

In NepCart, the recommendation system is an **Item-to-Item Collaborative Filtering Algorithm** based on the **Jaccard Similarity Coefficient**.

* **No Reviews or Star Ratings Needed:** Most traditional recommendation algorithms (like Pearson Correlation or Matrix Factorization) require users to give 1-to-5 star ratings or write text reviews. Since **NepCart does not have reviews or star ratings**, those algorithms cannot work.
* **Implicit Behavioral Feedback:** Instead of asking users for feedback, our algorithm looks at **real actions**: what products shoppers actually add to their shopping carts and buy together.
* **Core Idea:** If customers frequently buy **Product A** together with **Product B**, the system learns that these two items are related. When another customer views **Product A**, the system automatically suggests **Product B** under **"Frequently Bought Together"**.

---

## 2. How Does It Work in NepCart? (Real Example)

Imagine three customers shopping on NepCart:

* **Customer 1:** Buys a **Gaming Laptop** and a **Wireless Mouse**.
* **Customer 2:** Buys a **Gaming Laptop** and a **Wireless Mouse**.
* **Customer 3:** Buys a **Gaming Laptop** and a **Mechanical Keyboard**.

Now, a **new customer (Customer 4)** visits the store and opens the product page for the **Gaming Laptop**:

1. The system checks past carts and sees that out of 3 customers who bought the Laptop:
   * **2 customers** also bought the **Wireless Mouse**.
   * **1 customer** also bought the **Mechanical Keyboard**.
2. The algorithm calculates that the **Wireless Mouse** has the highest co-occurrence score with the Laptop.
3. The product page for the Gaming Laptop automatically displays:
   > **Frequently Bought Together:**
   > 1. Wireless Mouse (Highest Match)
   > 2. Mechanical Keyboard (Second Match)

---

## 3. Mathematical Foundation

The algorithm calculates similarity using the **Jaccard Similarity Coefficient**, a standard mathematical formula used to measure the similarity between two finite sample sets:

$$\text{Jaccard Similarity}(A, B) = \frac{|U_A \cap U_B|}{|U_A \cup U_B|}$$

$$\text{Jaccard Similarity}(A, B) = \frac{\text{Number of users who bought BOTH Product A and Product B}}{\text{Total unique users who bought EITHER Product A or Product B}}$$

### Variable Definitions:
* $U_A$: The set of all shoppers/sessions who added or purchased **Product A**.
* $U_B$: The set of all shoppers/sessions who added or purchased **Product B**.
* $|U_A \cap U_B|$ (Intersection): The count of common shoppers who purchased **both items together**.
* $|U_A \cup U_B|$ (Union): The total number of unique shoppers across both items.
* **Score Range:** 
  * **$0.0$**: No customer has ever bought these two products together.
  * **$1.0$**: Every customer who bought Product A also bought Product B (identical purchase pattern).

---

## 4. In Which Files is It Implemented?

The recommendation engine is cleanly integrated across three core files in the project:

| File Path | Role in Recommendation System |
| :--- | :--- |
| [`store/recommendations.py`](file:///c:/Users/Nirajan/Documents/antigravity/hopeful-hawking/store/recommendations.py) | **Algorithm Core:** Contains `get_jaccard_recommendations()` which queries the database, calculates Jaccard scores, and sorts recommendations. |
| [`store/views.py`](file:///c:/Users/Nirajan/Documents/antigravity/hopeful-hawking/store/views.py) | **Controller:** Calls the recommendation function in `product_display()` and injects the top products into the page context. |
| [`store/templates/store/product-detail.html`](file:///c:/Users/Nirajan/Documents/antigravity/hopeful-hawking/store/templates/store/product-detail.html) | **Presentation:** Renders the responsive **"Frequently Bought Together"** cards with images, prices, discount badges, and links. |

---

## 5. How is It Implemented? (Step-by-Step Code Walkthrough)

### Step 1: Find All Past Shoppers Who Ever Bought This Product
First, the system queries the database (`CartItem`) to find **all past shoppers** (Customer A, Customer B, Customer C...) who previously added or bought this item:

```python
target_interactions = CartItem.objects.filter(product=target_product)
users_target = set()
for item in target_interactions:
    if item.user_id:
        users_target.add(f"u_{item.user_id}")
    elif item.cart_id:
        users_target.add(f"c_{item.cart_id}")
```
* **Plain explanation:** If you are currently viewing a Laptop, the system gathers the list of all **past customers** who ever bought or carted that Laptop.

---

### Step 2: Look at What ELSE Those Past Customers Bought
Next, the code checks the purchase history of those past shoppers to see what other items they bought along with the Laptop:

```python
for prod_id, users_candidate in product_users.items():
    intersection = len(users_target.intersection(users_candidate))
    if intersection > 0:
        union = len(users_target.union(users_candidate))
        score = intersection / union if union > 0 else 0
        similarities[prod_id] = score
```
* **Plain explanation:** 
  * The system checks: *"When past customers bought this Laptop, what other items did they put in their baskets?"*
  * If 10 past customers bought the Laptop, and 8 of them also bought a **Mouse**, the Mouse gets a high similarity score.
  * `intersection` = How many past customers bought **both** the Laptop and the other item.
  * `union` = Total past customers across either item.
  * `score` = `intersection / union` (Higher score = items frequently bought together by past shoppers).

---

### Step 3: Put the Best Matches at the Top
The code sorts all candidate products from highest score to lowest score:

```python
ranked_product_ids = sorted(similarities, key=similarities.get, reverse=True)
recommended_products = list(Product.objects.filter(id__in=ranked_product_ids, is_available=True))
```
* **Plain explanation:** The items most frequently paired with the current product are moved to the front of the list.

---

### Step 4: Handle New Products (Category Fallback)
If a product is brand new and nobody has bought it yet with anything else, the score list would be empty. 
To make sure the page is never blank, the code fills any remaining spots using items from the **same category**:

```python
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
```
* **Plain explanation:** If there are fewer than 4 recommendations, it grabs popular available items from the same category so the section always has 4 relevant items to display.

---

### Step 5: Send to the Webpage to Display
Finally, in `store/views.py`, the view calls this function and sends the resulting products to the template:

```python
def product_display(request, category_slug, product_slug):
    shapeandsize = ProductCustomSizeColor(product_slug)
    data = Product.objects.get(slug=product_slug)
    recommended_products = get_jaccard_recommendations(data, limit=4)
    return render(request, "store/product-detail.html", {
        'catogery': category.objects.all(),
        'data': data,
        'form': shapeandsize,
        'recommended_products': recommended_products
    })
```
And in `store/templates/store/product-detail.html`, an HTML loop displays each item card with its image, title, and price under **"Frequently Bought Together"**.

---

## 6. Summary for Viva & Defense

When asked: **"Explain your recommendation algorithm"**:
> *"Because NepCart does not have reviews or star ratings, we cannot use traditional rating-based algorithms like Pearson Correlation. Instead, we implemented Item-to-Item Collaborative Filtering using the Jaccard Similarity Coefficient based on real cart and order co-occurrences. The algorithm calculates the ratio of shoppers who bought both items together over total unique shoppers ($|A \cap B| / |A \cup B|$) and suggests the highest-scoring items under 'Frequently Bought Together'. If an item is brand new with no history, it automatically backfills with items from the same category to handle the cold-start problem."*
