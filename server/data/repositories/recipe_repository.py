from logging import Logger

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from server.data.repositories.base_repository_ import BaseRepository


class RecipeRepository(BaseRepository):

    def __init__(self):
        super().__init__()
        self.recipe_table = self.dynamodb.Table('recipe')
        self.logger = Logger(name="recipe_repository")

    def get_recipe(self, id, title):
        try:
            response = self.recipe_table.get_item(Key={"id": id, "title": title})
        except ClientError as err:
            self.logger.error(
                "Couldn't get recipe %s from table %s. Here's why: %s: %s",
                title,
                self.recipe_table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise
        else:
            return response

    def scan_recipe(self, query_string):
        recipes = []
        scan_kwargs = {
            "FilterExpression": Attr('ner').contains(query_string) or Attr('directions').contains(query_string) or Attr(
                'ingredients').contains(query_string)
        }

        try:
            done = False
            start_key = None
            while not done:
                if start_key:
                    scan_kwargs["ExclusiveStartKey"] = start_key
                response = self.recipe_table.scan(**scan_kwargs)
                recipes.extend(response.get("Items", []))
                start_key = response.get("LastEvaluatedKey", None)
                done = start_key in None
        except ClientError as err:
            self.logger.error(
                "Couldn't scan recipes for query %s. Here's why: %s: %s",
                query_string,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise
        else:
            return recipes

    def insert_recipe(self, recipe):
        try:
            response = self.recipe_table.put_item(
                Item={
                    'id': recipe.id,
                    'title': recipe.title,
                    'ingredients': recipe.ingredients,
                    'directions': recipe.directions
                }
            )
        except ClientError as err:
            self.logger.error(
                "Couldn't add recipe %s to table %s. Here's why: %s: %s",
                recipe.title,
                self.recipe_table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise
        else:
            return response

    def update_recipe(self, recipe):
        try:
            response = self.recipe_table.update_item(
                Key={"id": recipe.id, "title": recipe.title},
                UpdateExpression="set "
                                 "recipe.directions=:dir, "
                                 "recipe.ingredients=:ing",
                ExpressionAttributeValues={
                    ":dir": recipe.directions,
                    ":ing": recipe.ingredients,
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as err:
            self.logger.error(
                "Couldn't update recipe %s in table %s. Here's why: %s: %s",
                recipe.title,
                self.recipe_table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise
        else:
            return response

    def delete_recipe(self, recipe_id, title):
        try:
            response = self.recipe_table.delete_item(
                Key={
                    id: recipe_id,
                    title: title
                }
            )
        except ClientError as err:
            self.logger.error(
                "Couldn't delete recipe %s. Here's why: %s: %s",
                title,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise
        else:
            return response
