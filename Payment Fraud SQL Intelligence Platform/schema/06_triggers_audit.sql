SET search_path = fraud;

CREATE OR REPLACE FUNCTION write_audit_log()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    actor TEXT;
    primary_key TEXT;
BEGIN
    actor := coalesce(current_setting('app.actor', true), current_user);

    IF TG_TABLE_NAME = 'transactions' THEN
        primary_key := coalesce(NEW.transaction_id::text, OLD.transaction_id::text);
    ELSIF TG_TABLE_NAME = 'manual_reviews' THEN
        primary_key := coalesce(NEW.review_id::text, OLD.review_id::text);
    ELSIF TG_TABLE_NAME = 'chargebacks' THEN
        primary_key := coalesce(NEW.chargeback_id::text, OLD.chargeback_id::text);
    ELSE
        primary_key := 'unknown';
    END IF;

    INSERT INTO audit_log (
        table_name,
        operation,
        row_pk,
        changed_by,
        old_data,
        new_data
    )
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        primary_key,
        actor,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END
    );

    RETURN coalesce(NEW, OLD);
END;
$$;

CREATE TRIGGER audit_transactions_changes
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW EXECUTE FUNCTION write_audit_log();

CREATE TRIGGER audit_manual_reviews_changes
AFTER INSERT OR UPDATE OR DELETE ON manual_reviews
FOR EACH ROW EXECUTE FUNCTION write_audit_log();

CREATE TRIGGER audit_chargebacks_changes
AFTER INSERT OR UPDATE OR DELETE ON chargebacks
FOR EACH ROW EXECUTE FUNCTION write_audit_log();
