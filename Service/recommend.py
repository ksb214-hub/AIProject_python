def recommend_recipe(df, user_ingredients):
    recipe_scores = {}

    recipe_group = df.groupby("레시피")["재료"].apply(list)

    for recipe, ingredients in recipe_group.items():
        match_count = len(set(user_ingredients) & set(ingredients))
        total_count = len(ingredients)

        score = match_count / total_count if total_count > 0 else 0

        recipe_scores[recipe] = score

    return sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)
