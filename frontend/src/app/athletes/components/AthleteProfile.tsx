'use client'
import { useState, useEffect } from 'react';
import { getMyProfile, createMyProfile, updateMyProfile } from '@/lib/api/athletes';

interface AthleteData {
  id: number;
  name: string;
  surname: string;
  gender: string | null;
  date_of_birth: string | null;
  height: string | null;
  weight: string | null;
  email: string;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  created_at: string;
}

type FormState = {
  name: string;
  surname: string;
  gender: string;
  date_of_birth: string;
  height: string;
  weight: string;
  email: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
};

type Mode = 'loading' | 'create' | 'edit' | 'error';

const GENDER_OPTIONS = [
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' },
  { value: 'O', label: 'Other' },
];

const inputClass =
  'w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors';

const emptyForm = (email = ''): FormState => ({
  name: '',
  surname: '',
  gender: '',
  date_of_birth: '',
  height: '',
  weight: '',
  email,
  emergency_contact_name: '',
  emergency_contact_phone: '',
});

const profileToForm = (p: AthleteData): FormState => ({
  name: p.name ?? '',
  surname: p.surname ?? '',
  gender: p.gender ?? '',
  date_of_birth: p.date_of_birth ?? '',
  height: p.height ?? '',
  weight: p.weight ?? '',
  email: p.email ?? '',
  emergency_contact_name: p.emergency_contact_name ?? '',
  emergency_contact_phone: p.emergency_contact_phone ?? '',
});

export default function AthleteProfile() {
  const [mode, setMode] = useState<Mode>('loading');
  const [profile, setProfile] = useState<AthleteData | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm());
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getMyProfile()
      .then((result) => {
        if ('_noProfile' in result) {
          setForm(emptyForm(result.userEmail));
          setMode('create');
        } else {
          setProfile(result as AthleteData);
          setForm(profileToForm(result as AthleteData));
          setMode('edit');
        }
      })
      .catch(() => setMode('error'));
  }, []);

  const set = (field: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSaved(false);

    try {
      if (mode === 'create') {
        const created = await createMyProfile(form as unknown as Record<string, unknown>);
        setProfile(created);
        setForm(profileToForm(created));
        setMode('edit');
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      } else {
        const updated = await updateMyProfile(form as unknown as Record<string, unknown>);
        setProfile(updated);
        setForm(profileToForm(updated));
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch {
      setError(mode === 'create' ? 'Failed to create profile.' : 'Failed to save changes.');
    } finally {
      setSubmitting(false);
    }
  };

  if (mode === 'loading') return (
    <div className="flex items-center gap-2 text-sm text-gray-400 py-8">
      <div className="w-4 h-4 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
      Loading profile…
    </div>
  );

  if (mode === 'error') return (
    <div className="border border-dashed border-gray-200 rounded-xl p-10 text-center">
      <p className="text-sm text-gray-500 mb-1">Couldn't load your profile.</p>
      <p className="text-xs text-gray-400">Please check your connection and try again.</p>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {mode === 'create' && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl px-5 py-4">
          <p className="text-sm font-medium text-blue-800 mb-0.5">No profile found</p>
          <p className="text-xs text-blue-600">
            Fill in your details below to create your athlete profile.
          </p>
        </div>
      )}

      {/* Personal */}
      <div className="border border-gray-100 rounded-xl p-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Personal information</p>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">
              First name <span className="text-red-400">*</span>
            </label>
            <input type="text" value={form.name} onChange={set('name')} required className={inputClass} placeholder="Jane" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">
              Surname <span className="text-red-400">*</span>
            </label>
            <input type="text" value={form.surname} onChange={set('surname')} required className={inputClass} placeholder="Smith" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Gender</label>
            <select value={form.gender} onChange={set('gender')} className={`${inputClass} bg-white`}>
              <option value="">Select gender</option>
              {GENDER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Date of birth</label>
            <input type="date" value={form.date_of_birth} onChange={set('date_of_birth')} className={inputClass} />
          </div>
        </div>
      </div>

      {/* Physical */}
      <div className="border border-gray-100 rounded-xl p-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Physical</p>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Height (cm)</label>
            <input
              type="number" step="0.01" min="0"
              value={form.height} onChange={set('height')}
              className={inputClass} placeholder="175.00"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Weight (kg)</label>
            <input
              type="number" step="0.01" min="0"
              value={form.weight} onChange={set('weight')}
              className={inputClass} placeholder="75.00"
            />
          </div>
        </div>
      </div>

      {/* Contact */}
      <div className="border border-gray-100 rounded-xl p-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Contact</p>
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-gray-600 mb-1.5">
              Email <span className="text-red-400">*</span>
            </label>
            <input
              type="email" value={form.email} onChange={set('email')} required
              readOnly={mode === 'edit'}
              className={`${inputClass} ${mode === 'edit' ? 'bg-gray-50 text-gray-500 cursor-default' : ''}`}
            />
            {mode === 'create' && (
              <p className="mt-1 text-xs text-gray-400">Must match your account email.</p>
            )}
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Emergency contact name</label>
            <input
              type="text" value={form.emergency_contact_name} onChange={set('emergency_contact_name')}
              className={inputClass} placeholder="Jane Smith"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Emergency contact phone</label>
            <input
              type="tel" value={form.emergency_contact_phone} onChange={set('emergency_contact_phone')}
              className={inputClass} placeholder="+44 7700 900000"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">{error}</div>
      )}
      {saved && (
        <div className="px-4 py-3 bg-green-50 border border-green-100 text-green-700 text-sm rounded-lg">
          {mode === 'edit' ? 'Profile saved.' : 'Profile created successfully.'}
        </div>
      )}

      <div className="flex items-center gap-4">
        <button
          type="submit"
          disabled={submitting}
          className="bg-gray-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting
            ? (mode === 'create' ? 'Creating…' : 'Saving…')
            : (mode === 'create' ? 'Create profile' : 'Save changes')}
        </button>
        {profile && (
          <p className="text-xs text-gray-400">
            Member since {new Date(profile.created_at).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}
          </p>
        )}
      </div>
    </form>
  );
}
