from django.db import connection
from django import template
from tree_menu.models import MenuItem

register = template.Library()

@register.simple_tag()
def draw_menu(name: str):
    connection.queries.clear()
    current_menu = MenuItem.objects.select_related('parent').prefetch_related('children').get(pk=name)
    top_ancestor = current_menu.parent or current_menu
    parents = [top_ancestor, ]
    while top_ancestor.parent:
        parents.append(top_ancestor)
        top_ancestor = top_ancestor.parent

    def build_menu(menu: MenuItem) -> str:
        builded_menu = '<li><a href="/{}"{}>{}</a>'.format(
            menu.pk, 'class="active"' if current_menu == menu else '', menu.title
        )
        builded_menu += build_menu_skeleton(menu.children.all(), depth=0)
        return builded_menu

    def build_menu_skeleton(items: list[MenuItem], depth: int) -> str:
        menu = ''
        max_depth = len(parents)
        ancestors = parents[2:] + [parents[-1]] + [current_menu.parent]
        children = parents + list(current_menu.children.all())

        for item in items:
            is_current_menu = item == current_menu
            is_same_country = item.parent == parents[-1].parent
            is_ancestor_or_descendant = item.parent in ancestors or item in children

            if is_current_menu:
                menu += '<li class="list-group-item"><a class="active" href="/{0}">{1}</a></li>'.format(
                    item.pk, item.title
                )
                if item.children.exists() and depth < max_depth:
                    other = build_menu_skeleton(item.children.all(), depth + 1)
                    if other:
                        menu += '<ul>{}</ul>'.format(other)

            elif is_same_country or is_ancestor_or_descendant:
                menu += '<li class="list-group-item"><a href="/{0}">{1}</a></li>'.format(
                    item.id, item.title
                )

                if item in parents and depth < max_depth:
                    other = build_menu_skeleton(item.children.all(), depth + 1)
                    if other:
                        menu += '<ul>{}</ul>'.format(other)

        return menu

    num_queries = len(connection.queries)
    menu = build_menu(top_ancestor)
    stat = f"<h1>Запросов в БД: {num_queries}</h1>"
    return stat + menu
