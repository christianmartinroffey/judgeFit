'use client'
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Trash2 } from 'lucide-react';
import AdminProtectedPage from '../../components/AdminProtectedPage';
import { getAthlete, updateAthlete, deleteAthlete } from '@/lib/api/athletes';

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
  profile_photo: string | null;
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

const GENDER_OPTIONS = [
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' },
  { value: 'O', label: 'Other' },
];

const inputClass =
  'w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors';

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

function AthleteDetailContent() {
  const { id } = useParams<{ id: string }>();
  const athleteId = parseInt(id);
  const router = useRouter();

  const [profile, setProfile] = useState<AthleteData | null>(null);
  const [form, setForm] = useState<FormState | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!athleteId) return;
    getAthlete(athleteId)
      .then((data) => {
        setProfile(data);
        setForm(profileToForm(data));
      })
      .catch(() => setError('Failed to load athlete.'))
      .finally(() => setLoading(false));
  }, [athleteId]);

  const set = (field: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => (prev ? { ...prev, [field]: e.target.value } : prev));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form) return;
    setSubmitting(true);
    setError(null);
    setSaved(false);
    try {
      const updated = await updateAthlete(athleteId, form as unknown as Record<string, unknown>);
      setProfile(updated);
      setForm(profileToForm(updated));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      setError('Failed to save changes.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteAthlete(athleteId);
      router.push('/athletes/roster');
    } catch {
      setError('Failed to delete athlete.');
      setDeleting(false);
    }
  };

  if (loading) return (
    <main className="min-h-screen bg-white flex items-center justify-center">
      <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
    </main>
  );

  if (error && !form) return (
    <main className="min-h-screen bg-white flex items-center justify-center">
      <p className="text-sm text-red-500">{error}</p>
    </main>
  );

  if (!form) return null;

  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <Link
          href="/athletes/roster"
          className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-900 transition-colors mb-8"
        >
          <ArrowLeft size={14} />
          Athletes
        </Link>

        <div className="flex items-center gap-4 mb-8">
          {profile?.profile_photo ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={profile.profile_photo} alt="" className="w-14 h-14 rounded-full object-cover border border-gray-200" />
          ) : (
            <div className="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 text-lg font-semibold">
              {form.name ? form.name.charAt(0).toUpperCase() : '?'}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              {form.name || form.surname ? `${form.name} ${form.surname}`.trim() : `Athlete #${athleteId}`}
            </h1>
            <p className="text-sm text-gray-500">{form.email}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="border border-gray-100 rounded-xl p-6">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Personal information</p>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">First name</label>
                <input type="text" value={form.name} onChange={set('name')} required className={inputClass} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Surname</label>
                <input type="text" value={form.surname} onChange={set('surname')} required className={inputClass} />
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

          <div className="border border-gray-100 rounded-xl p-6">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Physical</p>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Height (cm)</label>
                <input type="number" step="0.01" min="0" value={form.height} onChange={set('height')} className={inputClass} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Weight (kg)</label>
                <input type="number" step="0.01" min="0" value={form.weight} onChange={set('weight')} className={inputClass} />
              </div>
            </div>
          </div>

          <div className="border border-gray-100 rounded-xl p-6">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Contact</p>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Email</label>
                <input type="email" value={form.email} onChange={set('email')} required className={inputClass} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Emergency contact name</label>
                <input type="text" value={form.emergency_contact_name} onChange={set('emergency_contact_name')} className={inputClass} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Emergency contact phone</label>
                <input type="tel" value={form.emergency_contact_phone} onChange={set('emergency_contact_phone')} className={inputClass} />
              </div>
            </div>
          </div>

          {error && (
            <div className="px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">{error}</div>
          )}
          {saved && (
            <div className="px-4 py-3 bg-green-50 border border-green-100 text-green-700 text-sm rounded-lg">Saved.</div>
          )}

          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={submitting}
              className="bg-gray-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Saving…' : 'Save changes'}
            </button>

            {!confirmingDelete ? (
              <button
                type="button"
                onClick={() => setConfirmingDelete(true)}
                className="inline-flex items-center gap-1.5 text-sm text-red-500 hover:text-red-700 transition-colors"
              >
                <Trash2 size={14} />
                Delete athlete
              </button>
            ) : (
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-500">Delete this athlete?</span>
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="text-sm font-medium text-red-600 hover:text-red-800 transition-colors disabled:opacity-50"
                >
                  {deleting ? 'Deleting…' : 'Confirm'}
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmingDelete(false)}
                  className="text-sm text-gray-400 hover:text-gray-700 transition-colors"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </form>
      </div>
    </main>
  );
}

export default function AthleteDetailPage() {
  return (
    <AdminProtectedPage>
      <AthleteDetailContent />
    </AdminProtectedPage>
  );
}
