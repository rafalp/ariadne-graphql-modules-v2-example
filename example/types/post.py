from typing import TYPE_CHECKING, Annotated, Optional

from ariadne_graphql_modules import GraphQLObject, deferred
from ariadne import gql
from graphql import GraphQLResolveInfo

from ..database import db
from ..interfaces.search_result import SearchResultInterface
from ..models.category import Category
from ..models.post import Post
from ..models.user import User
from .category import CategoryType

if TYPE_CHECKING:
    from .user import UserType


class PostType(GraphQLObject):
    __schema__ = gql(
        """
        type Post implements SearchResultInterface {
            id: ID!
            content: String!
            category: Category
            poster: User
            summary: String!
        }
        """
    )
    __aliases__ = {"content": "message"}
    __requires__ = [SearchResultInterface]

    @GraphQLObject.resolver("category", CategoryType)
    @staticmethod
    async def resolve_category(obj: Post, info: GraphQLResolveInfo) -> Category:
        return await db.get_row("categories", id=obj.category_id)

    @GraphQLObject.resolver(
        "poster", Optional[Annotated["UserType", deferred(".user")]]
    )
    @staticmethod
    async def resolve_poster(obj: Post, info: GraphQLResolveInfo) -> User | None:
        if not obj.poster_id:
            return None

        return await db.get_row("users", id=obj.poster_id)

    @GraphQLObject.resolver("summary")
    @staticmethod
    async def resolve_summary(obj: Post, info: GraphQLResolveInfo):
        return f"#{obj.id}: {obj.message}"
