class EmailService:
    @staticmethod
    def send_welcome_email(to_email: str, username: str) -> None:
        """Placeholder for sending a welcome email on user registration."""
        print(f"[EmailService] email sent to {to_email}: Welcome to SkillBoost, {username}!")

    @staticmethod
    def send_join_request_email(to_email: str, applicant_username: str, clan_name: str) -> None:
        """Placeholder for notifying clan creator when a join application is created."""
        print(f"[EmailService] email sent to {to_email}: User '{applicant_username}' submitted a join application for clan '{clan_name}'!")
