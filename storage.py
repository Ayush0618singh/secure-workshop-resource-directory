import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "resources.json"


def _ensure_data_file():
    """
    Ensure that the data directory and JSON file exist.
    """
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_resources():
    """
    Load all workshop resources safely from the JSON dataset.
    """
    _ensure_data_file()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("resources.json must contain a JSON list.")

        return data

    except (json.JSONDecodeError, OSError, ValueError) as exc:
        raise RuntimeError(
            f"Could not read resource data safely: {exc}"
        ) from exc


def save_resources(resources):
    """
    Save the complete resource list.

    A temporary file is used first so that an interrupted write is
    less likely to corrupt the main dataset.
    """
    _ensure_data_file()

    if not isinstance(resources, list):
        raise ValueError("Resources must be stored as a list.")

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=DATA_FILE.parent,
            prefix="resources_",
            suffix=".tmp",
        ) as temp_file:

            json.dump(
                resources,
                temp_file,
                indent=2,
                ensure_ascii=False,
            )

            temp_path = Path(temp_file.name)

        os.replace(temp_path, DATA_FILE)

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def get_resource(resource_id):
    """
    Find one resource using its unique ID.
    """
    return next(
        (
            item
            for item in load_resources()
            if item.get("id") == resource_id
        ),
        None,
    )


def create_resource(resource_data):
    """
    Create and persist a new workshop resource.
    """
    resources = load_resources()

    new_resource = {
        "id": f"RES-{uuid4().hex[:8].upper()}",
        **resource_data,
    }

    resources.append(new_resource)

    save_resources(resources)

    return new_resource


def update_resource(resource_id, resource_data):
    """
    Update an existing resource.
    """
    resources = load_resources()

    for index, resource in enumerate(resources):

        if resource.get("id") == resource_id:

            updated_resource = {
                **resource,
                **resource_data,
                "id": resource_id,
            }

            resources[index] = updated_resource

            save_resources(resources)

            return updated_resource

    return None


def delete_resource(resource_id):
    """
    Delete one resource and return the deleted record.
    """
    resources = load_resources()

    for resource in resources:

        if resource.get("id") == resource_id:

            remaining_resources = [
                item
                for item in resources
                if item.get("id") != resource_id
            ]

            save_resources(remaining_resources)

            return resource

    return None