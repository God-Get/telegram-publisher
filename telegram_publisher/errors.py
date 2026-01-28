class PublisherError(Exception):
    """Base error for telegram-publisher."""


class TelegramAPIError(PublisherError):
    """Raised when Telegram returns an error we decide to surface."""
