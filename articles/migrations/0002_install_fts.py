from django.db import migrations

SQL = [
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS article_fts USING fts5(
        article_id UNINDEXED,
        title,
        body
    );
    """,
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
]

DROP = [
    'DROP TRIGGER IF EXISTS article_fts_ai;',
    'DROP TRIGGER IF EXISTS article_fts_au;',
    'DROP TRIGGER IF EXISTS article_fts_ad;',
    'DROP TABLE IF EXISTS article_fts;',
]


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(SQL, reverse_sql=DROP),
    ]
