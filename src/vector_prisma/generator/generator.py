import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..client import PACKAGED_SCHEMA_PATH

GENERATE_FILES = {
    "types.py.jinja": Path(__file__).parent.parent.joinpath("types_test.py"),
    "vectors.py.jinja": Path(__file__).parent.parent.joinpath("vectors_test.py"),
    "actions.py.jinja": Path(__file__).parent.parent.joinpath("actions_test.py"),
    "client.py.jinja": Path(__file__).parent.parent.joinpath("client_test.py"),
    "models.py.jinja": Path(__file__).parent.parent.joinpath("models_test.py"),
}

DEFAULT_ENV = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    undefined=StrictUndefined,
)


def regex_search(value, pattern):
    match = re.search(pattern, value)
    return match.groups() if match else []


DEFAULT_ENV.filters["regex_search"] = regex_search


def read_schema(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_tables_with_vector_type(
    schema: str,
) -> list[dict[str, list[dict[str, str | Any | bool | None]] | str | Any]]:
    tables = []
    table_pattern = re.compile(r"model (\w+) \{(.*?)\}", re.S)
    field_pattern = re.compile(r"(\w+)\s+([^\s]+)(.*)")

    for table_match in table_pattern.finditer(schema):
        table_name = table_match.group(1)
        table_body = table_match.group(2)

        fields = []
        has_vector_field = False
        seen_fields = set()
        for field_match in field_pattern.finditer(table_body):
            field_name = field_match.group(1)
            field_type = field_match.group(2)
            attributes = field_match.group(3).strip()

            if field_name in seen_fields:
                continue
            seen_fields.add(field_name)

            is_relation = (
                re.match(r"\w+", field_type)
                and not field_type.startswith("String")
                and not field_type.startswith("Int")
                and not field_type.startswith("Float")
                and not field_type.startswith("Boolean")
                and not field_type.startswith("DateTime")
                and not field_type.startswith("Unsupported")
            )

            fields.append(
                {
                    "name": field_name,
                    "type": field_type,
                    "attributes": attributes,
                    "relation": is_relation,
                }
            )

            if "Unsupported" in field_type and "vector" in field_type:
                has_vector_field = True

        if has_vector_field:
            tables.append({"table": table_name, "fields": fields})

    return tables


def transform_to_dmmf_format(json_data):
    models = []
    for table in json_data:
        fields = []
        for field in table["fields"]:
            fields.append(
                {
                    "name": field["name"],
                    "type": field["type"],
                    "is_relation": field["relation"],
                    "is_required": True,
                }
            )
        models.append(
            {
                "name": table["table"],
                "all_fields": fields,
            }
        )
    return {"datamodel": {"models": models}}


def generate_files(
    dmmf_data: dict[str, list[dict[str, list[dict[str, str]]]]],
    generate_files: dict[str, Path],
) -> None:
    env = DEFAULT_ENV
    for template_path, file_path in generate_files.items():
        template = env.get_template(template_path)
        content = template.render(**dmmf_data)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def save_output(file_paths: list[Path], content: str) -> None:
    for file_path in file_paths:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Error saving file: {file_path}")
            print(e)


if __name__ == "__main__":
    schema_path = PACKAGED_SCHEMA_PATH

    schema_content = read_schema(schema_path)
    tables_with_vectors = extract_tables_with_vector_type(schema_content)

    dmmf_data = transform_to_dmmf_format(tables_with_vectors)

    generate_files(dmmf_data, GENERATE_FILES)

    print("Files generated and saved")
