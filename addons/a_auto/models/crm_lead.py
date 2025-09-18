from odoo import api, fields, models
from datetime import timedelta

class CrmLead(models.Model):
    _inherit = "crm.lead"

    last_inactivity_reminder = fields.Datetime(
        string="Last Inactivity Reminder",
        readonly=True,
        copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        # Send welcome email to each new lead, if template exists and lead has an email
        template = self.env.ref(
            "dm_crm_automation.mail_template_lead_welcome",
            raise_if_not_found=False
        )
        if template:
            for lead in leads:
                # send only if there's an email to reach
                if lead.email_from or (lead.partner_id and lead.partner_id.email):
                    template.send_mail(lead.id, force_send=True)
        return leads

    @api.model
    def cron_send_inactivity_reminders(self):
        """Daily job: send reminder for leads inactive for N days and not Won/Lost."""
        icp = self.env["ir.config_parameter"].sudo()
        days = int(icp.get_param("dm_crm_automation.inactivity_days", default="7"))
        now = fields.Datetime.now()
        cutoff = now - timedelta(days=days)

        # Open leads/opportunities (not won, not lost, active)
        domain = [
            ("active", "=", True),
            ("probability", "<", 100),  # not fully won
            ("type", "in", ["lead", "opportunity"]),
            ("write_date", "<=", cutoff),
            "|", ("last_inactivity_reminder", "=", False),
                 ("last_inactivity_reminder", "<=", cutoff),
        ]
        candidates = self.search(domain, limit=1000)  # keep it safe; adjust as needed
        template = self.env.ref(
            "dm_crm_automation.mail_template_lead_inactivity",
            raise_if_not_found=False
        )
        if not template or not candidates:
            return

        for lead in candidates:
            if lead.email_from or (lead.partner_id and lead.partner_id.email):
                template.send_mail(lead.id, force_send=True)
                lead.last_inactivity_reminder = now

        # --- Optional SMS / WhatsApp (Twilio) example hook ---
        # if icp.get_param("dm_crm_automation.enable_sms") == "1":
        #     self._send_sms_batch(candidates)
        # if icp.get_param("dm_crm_automation.enable_whatsapp") == "1":
        #     self._send_whatsapp_batch(candidates)

    # Example stubs if you want to later wire Twilio (keep commented until configured)
    # def _send_sms_batch(self, leads):
    #     pass
    #
    # def _send_whatsapp_batch(self, leads):
    #     pass
