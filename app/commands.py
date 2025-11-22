import click
from flask.cli import with_appcontext
from .extensions import db
from .models import Document, Index
from .engine import engine

@click.command("download_nltk")
@with_appcontext
def download_nltk():
    """Download NLTK dictionaries"""
    engine.download_nltk_dicts()
    click.echo("NLTK dictionaries downloaded.")


@click.command("populate_db")
@with_appcontext
def populate_db_cmd():
    """Populate the database."""
    if not Document.query.first() and not Index.query.first():
        import init_db
        engine.index_all_documents()

        click.echo("Database populated.")


@click.command("reset_db")
@with_appcontext
def reset_db_cmd():
    """Reset the database."""
    db.drop_all()
    db.create_all()
    click.echo("Database reset.")
