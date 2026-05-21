# app/filters.py
import datetime


def register_filters(app):
    @app.template_filter('datetime')
    def format_datetime(timestamp):
        """Convert a timestamp to formatted date and time."""
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @app.template_filter('filesize')
    def format_filesize(size):
        """Format file size to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    # Add your third filter here