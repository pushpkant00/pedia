from django.db import migrations

SQL = [
    # 0003 rebuilds articles_article on SQLite, which drops these triggers.
    """
    CREATE TRIGGER IF NOT EXISTS article_fts_ai AFTER INSERT ON articles_article BEGIN
        INSERT INTO article_fts(article_id, title, body)
        VALUES (new.id, new.title, new.text_content);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS article_fts_au AFTER UPDATE ON articles_article BEGIN
        DELETE FROM article_fts WHERE article_id = old.id;
        INSERT INTO article_fts(article_id, title, body)
        VALUES (new.id, new.title, new.text_content);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS article_fts_ad AFTER DELETE ON articles_article BEGIN
        DELETE FROM article_fts WHERE article_id = old.id;
    END;
    """,
    # Rebuild the index so it matches the articles table exactly.
    'DELETE FROM article_fts;',
    'INSERT INTO article_fts(article_id, title, body) '
    'SELECT id, title, text_content FROM articles_article;',
]

DROP = [
    'DROP TRIGGER IF EXISTS article_fts_ai;',
    'DROP TRIGGER IF EXISTS article_fts_au;',
    'DROP TRIGGER IF EXISTS article_fts_ad;',
]


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_article_created_by_article_is_pending_and_more'),
    ]

    operations = [
        migrations.RunSQL(SQL, reverse_sql=DROP),
    ]
