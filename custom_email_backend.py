
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
from django.core.mail.backends.smtp import DNS_NAME


class EmailBackend(DjangoEmailBackend):

    def open(self):
        """
        Open an SMTP connection compatible with Python 3.12.
        """

        if self.connection:
            return False

        connection_params = {
            'local_hostname': DNS_NAME.get_fqdn()
        }

        if self.timeout is not None:
            connection_params['timeout'] = self.timeout

        try:
            self.connection = self.connection_class(
                self.host,
                self.port,
                **connection_params
            )

            if not self.use_ssl and self.use_tls:
                self.connection.starttls()

            if self.username and self.password:
                self.connection.login(
                    self.username,
                    self.password
                )

            return True

        except OSError:
            if not self.fail_silently:
                raise
