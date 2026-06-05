import { useState } from 'react';

const initialState = {
  author: '',
  yesterday: '',
  today: '',
  has_blocker: false,
  blockers: '',
  attachment: null,
};

function StandupForm({ onSubmit }) {
  const [fields, setFields] = useState(initialState);
  const [status, setStatus] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value, type, checked, files } = event.target;
    if (name === 'attachment') {
      setFields((current) => ({ ...current, attachment: files?.[0] || null }));
      return;
    }

    if (type === 'checkbox') {
      setFields((current) => ({
        ...current,
        has_blocker: checked,
        blockers: checked ? current.blockers : '',
        attachment: checked ? current.attachment : null,
      }));
      return;
    }

    setFields((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setStatus(null);

    const formData = new FormData();
    formData.append('author', fields.author);
    formData.append('yesterday', fields.yesterday);
    formData.append('today', fields.today);
    formData.append('blockers', fields.has_blocker ? fields.blockers : '');
    if (fields.has_blocker && fields.attachment) {
      formData.append('attachment', fields.attachment);
    }

    const result = await onSubmit(formData);
    setSubmitting(false);

    if (result.success) {
      setStatus({ type: 'success', message: 'Standup submitted successfully.' });
      setFields(initialState);
    } else {
      setStatus({ type: 'error', message: result.message || 'Unable to submit standup.' });
    }
  }

  return (
    <form className="standup-form" onSubmit={handleSubmit}>
      <label>
        Your name
        <input
          name="author"
          value={fields.author}
          onChange={handleChange}
          required
          placeholder="e.g. Jane Doe"
        />
      </label>

      <label>
        Yesterday
        <textarea
          name="yesterday"
          value={fields.yesterday}
          onChange={handleChange}
          required
          placeholder="What did you complete yesterday?"
        />
      </label>

      <label>
        Today
        <textarea
          name="today"
          value={fields.today}
          onChange={handleChange}
          required
          placeholder="What will you work on today?"
        />
      </label>

      <label className="checkbox-label">
        <span className="checkbox-text">I have a blocker to report</span>
        <span className="checkbox-control">
          <input
            type="checkbox"
            name="has_blocker"
            checked={fields.has_blocker}
            onChange={handleChange}
          />
          <span className="checkbox-custom" />
        </span>
      </label>

      {fields.has_blocker ? (
        <>
          <label>
            Blockers
            <textarea
              name="blockers"
              value={fields.blockers}
              onChange={handleChange}
              required={fields.has_blocker}
              placeholder="Describe the issue or dependency"
            />
          </label>

          <label>
            Upload supporting file
            <input
              type="file"
              name="attachment"
              accept="image/png,image/jpeg,application/pdf"
              onChange={handleChange}
            />
          </label>
        </>
      ) : null}

      <button type="submit" disabled={submitting}>
        {submitting ? 'Submitting...' : 'Submit Standup'}
      </button>

      {status && (
        <div className={`notice ${status.type === 'error' ? 'notice-error' : 'notice-success'}`}>
          {status.message}
        </div>
      )}
    </form>
  );
}

export default StandupForm;
