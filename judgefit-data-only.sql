COPY public.athlete_affiliate (id, name, address, city, postal_code, website, state, crossfit_affiliate, crossfit_affiliate_since, created_at, photo, country_id) FROM stdin;
\.
COPY public.athlete_athlete (id, name, surname, gender, date_of_birth, height, weight, email, created_at, profile_photo, emergency_contact_name, emergency_contact_phone, affiliate_id, country_id) FROM stdin;
1	Christian	MR	M	2026-05-01	100.00	100.00	c.martinroffey@gmail.com	2026-05-27 16:23:47.867894+00				\N	\N
\.
COPY public.athlete_competition (id, name, start_date, end_date, location, description, is_active, created_at) FROM stdin;
1	Karen COMP	2026-05-27	2027-01-31	anywhere	it's KAREN baby	t	2026-05-27 16:12:43.87212+00
\.
COPY public.athlete_country (id, name, router_code, code) FROM stdin;
\.
COPY public.auth_group (id, name) FROM stdin;
\.
COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.
COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add Affiliate	6	add_affiliate
22	Can change Affiliate	6	change_affiliate
23	Can delete Affiliate	6	delete_affiliate
24	Can view Affiliate	6	view_affiliate
25	Can add Competition	7	add_competition
26	Can change Competition	7	change_competition
27	Can delete Competition	7	delete_competition
28	Can view Competition	7	view_competition
29	Can add Country	8	add_country
30	Can change Country	8	change_country
31	Can delete Country	8	delete_country
32	Can view Country	8	view_country
33	Can add Athlete	9	add_athlete
34	Can change Athlete	9	change_athlete
35	Can delete Athlete	9	delete_athlete
36	Can view Athlete	9	view_athlete
37	Can add movement	10	add_movement
38	Can change movement	10	change_movement
39	Can delete movement	10	delete_movement
40	Can view movement	10	view_movement
41	Can add workout	11	add_workout
42	Can change workout	11	change_workout
43	Can delete workout	11	delete_workout
44	Can view workout	11	view_workout
45	Can add workout component	12	add_workoutcomponent
46	Can change workout component	12	change_workoutcomponent
47	Can delete workout component	12	delete_workoutcomponent
48	Can view workout component	12	view_workoutcomponent
49	Can add score	13	add_score
50	Can change score	13	change_score
51	Can delete score	13	delete_score
52	Can view score	13	view_score
53	Can add video	14	add_video
54	Can change video	14	change_video
55	Can delete video	14	delete_video
56	Can view video	14	view_video
57	Can add score breakdown	15	add_scorebreakdown
58	Can change score breakdown	15	change_scorebreakdown
59	Can delete score breakdown	15	delete_scorebreakdown
60	Can view score breakdown	15	view_scorebreakdown
61	Can add user	16	add_user
62	Can change user	16	change_user
63	Can delete user	16	delete_user
64	Can view user	16	view_user
65	Can add task result	17	add_taskresult
66	Can change task result	17	change_taskresult
67	Can delete task result	17	delete_taskresult
68	Can view task result	17	view_taskresult
69	Can add chord counter	18	add_chordcounter
70	Can change chord counter	18	change_chordcounter
71	Can delete chord counter	18	delete_chordcounter
72	Can view chord counter	18	view_chordcounter
73	Can add group result	19	add_groupresult
74	Can change group result	19	change_groupresult
75	Can delete group result	19	delete_groupresult
76	Can view group result	19	view_groupresult
77	Can add crontab	20	add_crontabschedule
78	Can change crontab	20	change_crontabschedule
79	Can delete crontab	20	delete_crontabschedule
80	Can view crontab	20	view_crontabschedule
81	Can add interval	21	add_intervalschedule
82	Can change interval	21	change_intervalschedule
83	Can delete interval	21	delete_intervalschedule
84	Can view interval	21	view_intervalschedule
85	Can add periodic task	22	add_periodictask
86	Can change periodic task	22	change_periodictask
87	Can delete periodic task	22	delete_periodictask
88	Can view periodic task	22	view_periodictask
89	Can add periodic task track	23	add_periodictasks
90	Can change periodic task track	23	change_periodictasks
91	Can delete periodic task track	23	delete_periodictasks
92	Can view periodic task track	23	view_periodictasks
93	Can add solar event	24	add_solarschedule
94	Can change solar event	24	change_solarschedule
95	Can delete solar event	24	delete_solarschedule
96	Can view solar event	24	view_solarschedule
97	Can add clocked	25	add_clockedschedule
98	Can change clocked	25	change_clockedschedule
99	Can delete clocked	25	delete_clockedschedule
100	Can view clocked	25	view_clockedschedule
\.
COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2026-05-27 16:12:43.874236+00	1	Competition object (1)	1	[{"added": {}}]	7	1
2	2026-05-27 16:21:28.442574+00	1	Karen	1	[{"added": {}}]	11	1
3	2026-05-27 16:41:00.738267+00	1	wall ball	1	[{"added": {}}]	10	1
4	2026-05-27 16:41:14.473052+00	1	WorkoutComponent object (1)	1	[{"added": {}}]	12	1
\.
COPY public.django_celery_beat_clockedschedule (id, clocked_time) FROM stdin;
\.
COPY public.django_celery_beat_crontabschedule (id, minute, hour, day_of_week, day_of_month, month_of_year, timezone) FROM stdin;
1	0	4	*	*	*	UTC
\.
COPY public.django_celery_beat_intervalschedule (id, every, period) FROM stdin;
\.
COPY public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) FROM stdin;
1	celery.backend_cleanup	celery.backend_cleanup	[]	{}	\N	\N	\N	\N	t	2026-06-07 19:44:40.819212+00	5	2026-06-07 19:44:40.835283+00		1	\N	\N	f	\N	\N	{}	\N	43200
\.
COPY public.django_celery_beat_periodictasks (ident, last_update) FROM stdin;
1	2026-06-07 19:44:40.795644+00
\.
COPY public.django_celery_beat_solarschedule (id, event, latitude, longitude) FROM stdin;
\.
COPY public.django_celery_results_chordcounter (id, group_id, sub_tasks, count) FROM stdin;
\.
COPY public.django_celery_results_groupresult (id, group_id, date_created, date_done, content_type, content_encoding, result) FROM stdin;
\.
COPY public.django_celery_results_taskresult (id, task_id, status, content_type, content_encoding, result, date_done, traceback, meta, task_args, task_kwargs, task_name, worker, date_created, periodic_task_name) FROM stdin;
33	fc1ee574-0ede-4d4d-ad04-a556e9df684f	SUCCESS	application/json	utf-8	null	2026-06-07 19:44:41.798529+00	\N	{"children": []}	\N	\N	\N	\N	2026-06-07 19:44:41.798524+00	\N
\.
COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	athlete	affiliate
7	athlete	competition
8	athlete	country
9	athlete	athlete
10	workout	movement
11	workout	workout
12	workout	workoutcomponent
13	workout	score
14	workout	video
15	workout	scorebreakdown
16	users	user
17	django_celery_results	taskresult
18	django_celery_results	chordcounter
19	django_celery_results	groupresult
20	django_celery_beat	crontabschedule
21	django_celery_beat	intervalschedule
22	django_celery_beat	periodictask
23	django_celery_beat	periodictasks
24	django_celery_beat	solarschedule
25	django_celery_beat	clockedschedule
\.
COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-05-27 07:00:04.635135+00
2	contenttypes	0002_remove_content_type_name	2026-05-27 07:00:04.639537+00
3	auth	0001_initial	2026-05-27 07:00:04.695288+00
4	auth	0002_alter_permission_name_max_length	2026-05-27 07:00:04.6982+00
5	auth	0003_alter_user_email_max_length	2026-05-27 07:00:04.701926+00
6	auth	0004_alter_user_username_opts	2026-05-27 07:00:04.705355+00
7	auth	0005_alter_user_last_login_null	2026-05-27 07:00:04.707803+00
8	auth	0006_require_contenttypes_0002	2026-05-27 07:00:04.71011+00
9	auth	0007_alter_validators_add_error_messages	2026-05-27 07:00:04.713111+00
10	auth	0008_alter_user_username_max_length	2026-05-27 07:00:04.725559+00
11	auth	0009_alter_user_last_name_max_length	2026-05-27 07:00:04.729047+00
12	auth	0010_alter_group_name_max_length	2026-05-27 07:00:04.732954+00
13	auth	0011_update_proxy_permissions	2026-05-27 07:00:04.759217+00
14	auth	0012_alter_user_first_name_max_length	2026-05-27 07:00:04.764113+00
15	users	0001_initial	2026-05-27 07:00:04.791035+00
16	admin	0001_initial	2026-05-27 07:00:04.803625+00
17	admin	0002_logentry_remove_auto_add	2026-05-27 07:00:04.807136+00
18	admin	0003_logentry_add_action_flag_choices	2026-05-27 07:00:04.811024+00
19	athlete	0001_initial	2026-05-27 07:00:04.837858+00
20	django_celery_beat	0001_initial	2026-05-27 07:00:04.857711+00
21	django_celery_beat	0002_auto_20161118_0346	2026-05-27 07:00:04.865202+00
22	django_celery_beat	0003_auto_20161209_0049	2026-05-27 07:00:04.871035+00
23	django_celery_beat	0004_auto_20170221_0000	2026-05-27 07:00:04.874429+00
24	django_celery_beat	0005_add_solarschedule_events_choices	2026-05-27 07:00:04.87726+00
25	django_celery_beat	0006_auto_20180322_0932	2026-05-27 07:00:04.892324+00
26	django_celery_beat	0007_auto_20180521_0826	2026-05-27 07:00:04.900039+00
27	django_celery_beat	0008_auto_20180914_1922	2026-05-27 07:00:04.911736+00
28	django_celery_beat	0006_auto_20180210_1226	2026-05-27 07:00:04.918919+00
29	django_celery_beat	0006_periodictask_priority	2026-05-27 07:00:04.924075+00
30	django_celery_beat	0009_periodictask_headers	2026-05-27 07:00:04.929335+00
31	django_celery_beat	0010_auto_20190429_0326	2026-05-27 07:00:04.982487+00
32	django_celery_beat	0011_auto_20190508_0153	2026-05-27 07:00:04.992473+00
33	django_celery_beat	0012_periodictask_expire_seconds	2026-05-27 07:00:04.996925+00
34	django_celery_beat	0013_auto_20200609_0727	2026-05-27 07:00:05.001782+00
35	django_celery_beat	0014_remove_clockedschedule_enabled	2026-05-27 07:00:05.006385+00
36	django_celery_beat	0015_edit_solarschedule_events_choices	2026-05-27 07:00:05.009271+00
37	django_celery_beat	0016_alter_crontabschedule_timezone	2026-05-27 07:00:05.013906+00
38	django_celery_beat	0017_alter_crontabschedule_month_of_year	2026-05-27 07:00:05.017988+00
39	django_celery_beat	0018_improve_crontab_helptext	2026-05-27 07:00:05.022832+00
40	django_celery_beat	0019_alter_periodictasks_options	2026-05-27 07:00:05.025248+00
41	django_celery_results	0001_initial	2026-05-27 07:00:05.034586+00
42	django_celery_results	0002_add_task_name_args_kwargs	2026-05-27 07:00:05.038816+00
43	django_celery_results	0003_auto_20181106_1101	2026-05-27 07:00:05.041263+00
44	django_celery_results	0004_auto_20190516_0412	2026-05-27 07:00:05.054499+00
45	django_celery_results	0005_taskresult_worker	2026-05-27 07:00:05.061735+00
46	django_celery_results	0006_taskresult_date_created	2026-05-27 07:00:05.072122+00
47	django_celery_results	0007_remove_taskresult_hidden	2026-05-27 07:00:05.075501+00
48	django_celery_results	0008_chordcounter	2026-05-27 07:00:05.083659+00
49	django_celery_results	0009_groupresult	2026-05-27 07:00:05.123163+00
50	django_celery_results	0010_remove_duplicate_indices	2026-05-27 07:00:05.12853+00
51	django_celery_results	0011_taskresult_periodic_task_name	2026-05-27 07:00:05.131662+00
52	sessions	0001_initial	2026-05-27 07:00:05.140242+00
53	users	0002_user_is_athlete	2026-05-27 07:00:05.14451+00
54	users	0003_user_is_competition_admin	2026-05-27 07:00:05.150331+00
55	workout	0001_initial	2026-05-27 07:00:05.174336+00
56	workout	0002_remove_score_athlete_remove_score_competition_and_more	2026-05-27 07:00:05.202771+00
57	workout	0003_alter_video_id	2026-05-27 07:00:05.207823+00
58	workout	0004_video_urlpath	2026-05-27 07:00:05.211967+00
59	workout	0005_add_score_status_and_movement_breakdown	2026-05-27 07:00:05.218416+00
60	workout	0006_add_round_to_workout_component	2026-05-27 07:00:05.226147+00
61	workout	0007_alter_score_is_valid	2026-05-27 07:00:05.229102+00
62	workout	0008_scorebreakdown	2026-05-27 07:00:05.240015+00
63	workout	0009_add_equipment_no_rep_reason	2026-05-27 07:00:05.24294+00
64	workout	0010_score_good_reps	2026-05-31 14:09:14.491424+00
\.
COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
el5ujsba8yo0mg5ba6nyr3wm8l0t8yb3	.eJxVjDsOwjAQBe_iGln-fyjpOYNl725wANlSnFSIu0OkFNC-mXkvlvK21rQNWtKM7MwkO_1uJcOD2g7wntutc-htXebCd4UfdPBrR3peDvfvoOZRv7WOGiEK6yYg66zD4oMr0k9BGu1AQzQFg1CoSAmSAZQNkWLxBtFDUOz9AdWKN48:1wSGrQ:Jc9uB0ROr9WlhnO55gGH3KpGQOh8C5oxsqNbBIzxri0	2026-06-10 16:12:00.604849+00
\.
COPY public.users_user (id, password, last_login, is_superuser, username, first_name, last_name, is_staff, is_active, date_joined, email, is_athlete, is_competition_admin) FROM stdin;
1	pbkdf2_sha256$600000$o0QAixUixTwtANnF3TBkOo$3J4LruHFZ4gig8bqO6+iaCxqMdcZKAGyerxYUl3NZoM=	2026-05-27 16:12:00.603899+00	t	christianmr			t	t	2026-05-27 16:10:07.228465+00	c.martinroffey@gmail.com	f	f
2	pbkdf2_sha256$600000$MmwBze7VkgXJDhmHM0ahmv$TVcnFF8uakCFN8a0hMfhKCbOxBjHdPRWPIWikZ027Bo=	\N	f	christianroffey			f	t	2026-05-31 17:28:10.02131+00	c.martinroffey@hotmail.com	f	f
\.
COPY public.users_user_groups (id, user_id, group_id) FROM stdin;
\.
COPY public.users_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.
COPY public.workout_movement (id, name, description, modality, type, body_part, equipment) FROM stdin;
1	wall ball	wall ball	W	CA	full body	wall ball
\.
COPY public.workout_score (id, is_valid, total_reps, no_reps, score, created_at, is_scaled, movement_breakdown, status, good_reps) FROM stdin;
1	t	16	5		2026-05-27 16:23:56.894872+00	f	[]	complete	\N
2	t	16	5		2026-05-27 16:28:55.48809+00	f	[]	complete	\N
26	f	5	2		2026-06-01 06:29:37.810525+00	f	[{"reps": 5, "round": 1, "no_reps": 2, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
3	t	16	5		2026-05-27 16:31:47.062965+00	f	[]	complete	\N
4	t	16	5		2026-05-27 16:34:25.995134+00	f	[]	complete	\N
5	t	16	5		2026-05-27 16:36:15.462774+00	f	[]	complete	\N
27	f	5	2		2026-06-01 06:48:34.191564+00	f	[{"reps": 5, "round": 1, "no_reps": 2, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
6	t	16	5		2026-05-27 16:38:19.052931+00	f	[]	complete	\N
7	f	\N	\N		2026-05-27 16:48:23.703118+00	f	[]	failed	\N
8	f	\N	\N		2026-05-27 17:21:44.021383+00	f	[]	failed	\N
28	f	7	2		2026-06-01 07:05:41.584064+00	f	[{"reps": 7, "round": 1, "no_reps": 2, "movement": "wall_ball", "sequence": 1, "good_reps": 5, "expected_reps": 150, "advance_reason": "video_end"}]	complete	5
9	f	\N	\N		2026-05-27 17:44:27.696816+00	f	[]	failed	\N
10	f	\N	\N		2026-05-27 17:49:23.217552+00	f	[]	failed	\N
11	f	\N	\N		2026-05-27 17:53:52.033618+00	f	[]	failed	\N
12	f	\N	\N		2026-05-27 18:08:11.732005+00	f	[]	failed	\N
13	f	\N	\N		2026-05-27 18:12:37.761969+00	f	[]	failed	\N
14	f	0	0		2026-05-27 18:21:32.193913+00	f	[{"reps": 0, "round": 1, "no_reps": 0, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
15	f	0	0		2026-05-27 18:39:11.68467+00	f	[{"reps": 0, "round": 1, "no_reps": 0, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
16	f	5	5		2026-05-28 06:36:04.933583+00	f	[{"reps": 5, "round": 1, "no_reps": 5, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
17	f	2	8		2026-05-28 06:50:20.820643+00	f	[{"reps": 2, "round": 1, "no_reps": 8, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
18	f	9	1		2026-05-28 07:04:36.465967+00	f	[{"reps": 9, "round": 1, "no_reps": 1, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
19	f	10	0		2026-05-28 07:21:21.123856+00	f	[{"reps": 10, "round": 1, "no_reps": 0, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
20	f	\N	\N		2026-05-30 19:03:49.097626+00	f	[]	failed	\N
21	f	\N	\N		2026-05-30 19:13:54.530851+00	f	[]	failed	\N
22	f	\N	\N		2026-05-30 19:15:23.948158+00	f	[]	failed	\N
23	f	10	0		2026-05-30 19:16:04.344899+00	f	[{"reps": 10, "round": 1, "no_reps": 0, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
24	t	150	3		2026-05-30 19:24:32.152743+00	f	[{"reps": 150, "round": 1, "no_reps": 3, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
25	t	150	3		2026-05-31 17:02:15.288121+00	f	[{"reps": 150, "round": 1, "no_reps": 3, "movement": "wall_ball", "sequence": 1, "expected_reps": 150, "advance_reason": "video_end"}]	complete	\N
\.
COPY public.workout_scorebreakdown (id, is_good_rep, no_rep_reason, created_at, rep_number, rep_timestamp, movement_id, score_id) FROM stdin;
1	t	\N	2026-05-28 06:38:28.780327+00	1	1	1	16
2	t	\N	2026-05-28 06:38:28.780409+00	2	3	1	16
3	f	Q	2026-05-28 06:38:28.780437+00	3	5	1	16
4	t	\N	2026-05-28 06:38:28.780447+00	4	7	1	16
5	f	Q	2026-05-28 06:38:28.780451+00	5	9	1	16
6	f	Q	2026-05-28 06:38:28.780519+00	6	11	1	16
7	f	Q	2026-05-28 06:38:28.780758+00	7	13	1	16
8	t	\N	2026-05-28 06:38:28.780788+00	8	15	1	16
9	t	\N	2026-05-28 06:38:28.780804+00	9	17	1	16
10	f	Q	2026-05-28 06:38:28.780809+00	10	19	1	16
11	f	Q	2026-05-28 06:55:55.989262+00	1	1	1	17
12	f	Q	2026-05-28 06:55:55.989299+00	2	3	1	17
13	f	Q	2026-05-28 06:55:55.989307+00	3	5	1	17
14	t	\N	2026-05-28 06:55:55.989346+00	4	7	1	17
15	t	\N	2026-05-28 06:55:55.989374+00	5	9	1	17
16	f	Q	2026-05-28 06:55:55.989381+00	6	11	1	17
17	f	Q	2026-05-28 06:55:55.989393+00	7	13	1	17
18	f	Q	2026-05-28 06:55:55.989402+00	8	15	1	17
19	f	Q	2026-05-28 06:55:55.989406+00	9	17	1	17
20	f	Q	2026-05-28 06:55:55.989411+00	10	19	1	17
21	t	\N	2026-05-28 07:09:56.812511+00	1	1	1	18
22	t	\N	2026-05-28 07:09:56.812597+00	2	3	1	18
23	t	\N	2026-05-28 07:09:56.812605+00	3	5	1	18
24	t	\N	2026-05-28 07:09:56.81261+00	4	7	1	18
25	t	\N	2026-05-28 07:09:56.812615+00	5	9	1	18
26	t	\N	2026-05-28 07:09:56.81262+00	6	11	1	18
27	t	\N	2026-05-28 07:09:56.812625+00	7	13	1	18
28	t	\N	2026-05-28 07:09:56.812629+00	8	15	1	18
29	f	Q	2026-05-28 07:09:56.812634+00	9	17	1	18
30	t	\N	2026-05-28 07:09:56.812639+00	10	19	1	18
31	t	\N	2026-05-28 07:26:45.22452+00	1	1	1	19
32	t	\N	2026-05-28 07:26:45.224557+00	2	3	1	19
33	t	\N	2026-05-28 07:26:45.224578+00	3	5	1	19
34	t	\N	2026-05-28 07:26:45.224585+00	4	7	1	19
35	t	\N	2026-05-28 07:26:45.224591+00	5	9	1	19
36	t	\N	2026-05-28 07:26:45.224607+00	6	11	1	19
37	t	\N	2026-05-28 07:26:45.22462+00	7	13	1	19
38	t	\N	2026-05-28 07:26:45.224626+00	8	15	1	19
39	t	\N	2026-05-28 07:26:45.224647+00	9	17	1	19
40	t	\N	2026-05-28 07:26:45.224659+00	10	19	1	19
41	t	\N	2026-05-30 19:23:05.828824+00	1	1	1	23
42	t	\N	2026-05-30 19:23:05.828843+00	2	3	1	23
43	t	\N	2026-05-30 19:23:05.828849+00	3	5	1	23
44	t	\N	2026-05-30 19:23:05.828855+00	4	7	1	23
45	t	\N	2026-05-30 19:23:05.82886+00	5	9	1	23
46	t	\N	2026-05-30 19:23:05.828865+00	6	11	1	23
47	t	\N	2026-05-30 19:23:05.828883+00	7	13	1	23
48	t	\N	2026-05-30 19:23:05.828889+00	8	15	1	23
49	t	\N	2026-05-30 19:23:05.828908+00	9	17	1	23
50	t	\N	2026-05-30 19:23:05.828914+00	10	19	1	23
51	t	\N	2026-05-30 23:53:16.287328+00	1	5	1	24
52	t	\N	2026-05-30 23:53:16.287344+00	2	6	1	24
53	t	\N	2026-05-30 23:53:16.28735+00	3	8	1	24
54	t	\N	2026-05-30 23:53:16.287355+00	4	9	1	24
55	t	\N	2026-05-30 23:53:16.28736+00	5	11	1	24
56	t	\N	2026-05-30 23:53:16.287365+00	6	13	1	24
57	t	\N	2026-05-30 23:53:16.28737+00	7	14	1	24
58	t	\N	2026-05-30 23:53:16.287374+00	8	16	1	24
59	t	\N	2026-05-30 23:53:16.287383+00	9	18	1	24
60	t	\N	2026-05-30 23:53:16.287388+00	10	20	1	24
61	t	\N	2026-05-30 23:53:16.287393+00	11	21	1	24
62	t	\N	2026-05-30 23:53:16.287397+00	12	23	1	24
63	t	\N	2026-05-30 23:53:16.287402+00	13	25	1	24
64	t	\N	2026-05-30 23:53:16.287406+00	14	28	1	24
65	t	\N	2026-05-30 23:53:16.287418+00	15	28	1	24
66	t	\N	2026-05-30 23:53:16.287424+00	16	30	1	24
67	t	\N	2026-05-30 23:53:16.287429+00	17	32	1	24
68	t	\N	2026-05-30 23:53:16.287433+00	18	34	1	24
69	t	\N	2026-05-30 23:53:16.287438+00	19	35	1	24
70	t	\N	2026-05-30 23:53:16.287442+00	20	37	1	24
71	t	\N	2026-05-30 23:53:16.287447+00	21	39	1	24
72	t	\N	2026-05-30 23:53:16.287451+00	22	41	1	24
73	t	\N	2026-05-30 23:53:16.287456+00	23	42	1	24
74	t	\N	2026-05-30 23:53:16.287461+00	24	44	1	24
75	t	\N	2026-05-30 23:53:16.287469+00	25	46	1	24
76	t	\N	2026-05-30 23:53:16.287474+00	26	48	1	24
77	t	\N	2026-05-30 23:53:16.287479+00	27	49	1	24
78	t	\N	2026-05-30 23:53:16.287484+00	28	51	1	24
79	t	\N	2026-05-30 23:53:16.287488+00	29	54	1	24
80	t	\N	2026-05-30 23:53:16.287493+00	30	55	1	24
81	t	\N	2026-05-30 23:53:16.287497+00	31	56	1	24
82	t	\N	2026-05-30 23:53:16.287502+00	32	58	1	24
83	t	\N	2026-05-30 23:53:16.287524+00	33	60	1	24
84	t	\N	2026-05-30 23:53:16.287539+00	34	61	1	24
85	t	\N	2026-05-30 23:53:16.287544+00	35	63	1	24
86	t	\N	2026-05-30 23:53:16.287549+00	36	65	1	24
87	t	\N	2026-05-30 23:53:16.287558+00	37	67	1	24
88	t	\N	2026-05-30 23:53:16.287563+00	38	68	1	24
89	t	\N	2026-05-30 23:53:16.287587+00	39	70	1	24
90	t	\N	2026-05-30 23:53:16.287703+00	40	72	1	24
91	t	\N	2026-05-30 23:53:16.287709+00	41	74	1	24
92	t	\N	2026-05-30 23:53:16.287714+00	42	75	1	24
93	t	\N	2026-05-30 23:53:16.287719+00	43	78	1	24
94	t	\N	2026-05-30 23:53:16.287724+00	44	79	1	24
95	t	\N	2026-05-30 23:53:16.287729+00	45	81	1	24
96	t	\N	2026-05-30 23:53:16.287733+00	46	82	1	24
97	t	\N	2026-05-30 23:53:16.287738+00	47	84	1	24
98	t	\N	2026-05-30 23:53:16.287743+00	48	86	1	24
99	t	\N	2026-05-30 23:53:16.287747+00	49	88	1	24
100	t	\N	2026-05-30 23:53:16.287752+00	50	90	1	24
101	t	\N	2026-05-30 23:53:16.287757+00	51	92	1	24
102	t	\N	2026-05-30 23:53:16.287761+00	52	94	1	24
103	t	\N	2026-05-30 23:53:16.287766+00	53	96	1	24
104	t	\N	2026-05-30 23:53:16.28777+00	54	97	1	24
105	t	\N	2026-05-30 23:53:16.287775+00	55	99	1	24
106	t	\N	2026-05-30 23:53:16.287779+00	56	100	1	24
107	t	\N	2026-05-30 23:53:16.287784+00	57	102	1	24
108	t	\N	2026-05-30 23:53:16.287788+00	58	105	1	24
109	t	\N	2026-05-30 23:53:16.287793+00	59	106	1	24
110	t	\N	2026-05-30 23:53:16.287797+00	60	108	1	24
111	t	\N	2026-05-30 23:53:16.287801+00	61	109	1	24
112	t	\N	2026-05-30 23:53:16.287806+00	62	111	1	24
113	t	\N	2026-05-30 23:53:16.28781+00	63	113	1	24
114	t	\N	2026-05-30 23:53:16.287815+00	64	115	1	24
115	t	\N	2026-05-30 23:53:16.287819+00	65	117	1	24
116	t	\N	2026-05-30 23:53:16.287824+00	66	119	1	24
117	t	\N	2026-05-30 23:53:16.287828+00	67	120	1	24
118	t	\N	2026-05-30 23:53:16.287832+00	68	122	1	24
119	t	\N	2026-05-30 23:53:16.287837+00	69	124	1	24
120	t	\N	2026-05-30 23:53:16.287841+00	70	126	1	24
121	t	\N	2026-05-30 23:53:16.287846+00	71	128	1	24
122	t	\N	2026-05-30 23:53:16.28785+00	72	130	1	24
123	t	\N	2026-05-30 23:53:16.287855+00	73	132	1	24
124	t	\N	2026-05-30 23:53:16.287859+00	74	133	1	24
125	t	\N	2026-05-30 23:53:16.287864+00	75	136	1	24
126	t	\N	2026-05-30 23:53:16.287868+00	76	137	1	24
127	t	\N	2026-05-30 23:53:16.287872+00	77	139	1	24
128	t	\N	2026-05-30 23:53:16.287877+00	78	141	1	24
129	t	\N	2026-05-30 23:53:16.287895+00	79	143	1	24
130	t	\N	2026-05-30 23:53:16.2879+00	80	145	1	24
131	t	\N	2026-05-30 23:53:16.287904+00	81	146	1	24
132	t	\N	2026-05-30 23:53:16.287909+00	82	149	1	24
133	t	\N	2026-05-30 23:53:16.287925+00	83	150	1	24
134	t	\N	2026-05-30 23:53:16.28793+00	84	152	1	24
135	t	\N	2026-05-30 23:53:16.287934+00	85	154	1	24
136	t	\N	2026-05-30 23:53:16.287939+00	86	157	1	24
137	t	\N	2026-05-30 23:53:16.287943+00	87	158	1	24
138	t	\N	2026-05-30 23:53:16.288009+00	88	160	1	24
139	t	\N	2026-05-30 23:53:16.288029+00	89	161	1	24
140	t	\N	2026-05-30 23:53:16.288034+00	90	163	1	24
141	t	\N	2026-05-30 23:53:16.288039+00	91	165	1	24
142	t	\N	2026-05-30 23:53:16.288043+00	92	167	1	24
143	t	\N	2026-05-30 23:53:16.288048+00	93	169	1	24
144	t	\N	2026-05-30 23:53:16.288095+00	94	171	1	24
145	t	\N	2026-05-30 23:53:16.288102+00	95	173	1	24
146	t	\N	2026-05-30 23:53:16.288107+00	96	175	1	24
147	t	\N	2026-05-30 23:53:16.288111+00	97	177	1	24
148	t	\N	2026-05-30 23:53:16.288116+00	98	178	1	24
149	t	\N	2026-05-30 23:53:16.28812+00	99	181	1	24
150	t	\N	2026-05-30 23:53:16.288125+00	100	182	1	24
151	t	\N	2026-05-30 23:53:16.288129+00	101	184	1	24
152	t	\N	2026-05-30 23:53:16.288133+00	102	187	1	24
153	t	\N	2026-05-30 23:53:16.288138+00	103	190	1	24
154	f	D	2026-05-30 23:53:16.288143+00	104	190	1	24
155	t	\N	2026-05-30 23:53:16.288147+00	105	192	1	24
156	t	\N	2026-05-30 23:53:16.288152+00	106	194	1	24
157	t	\N	2026-05-30 23:53:16.288156+00	107	196	1	24
158	t	\N	2026-05-30 23:53:16.288161+00	108	197	1	24
159	f	D	2026-05-30 23:53:16.288165+00	109	198	1	24
160	t	\N	2026-05-30 23:53:16.28817+00	110	200	1	24
161	t	\N	2026-05-30 23:53:16.288175+00	111	203	1	24
162	t	\N	2026-05-30 23:53:16.288179+00	112	205	1	24
163	t	\N	2026-05-30 23:53:16.288183+00	113	206	1	24
164	t	\N	2026-05-30 23:53:16.288188+00	114	208	1	24
165	t	\N	2026-05-30 23:53:16.288192+00	115	210	1	24
166	t	\N	2026-05-30 23:53:16.288197+00	116	211	1	24
167	t	\N	2026-05-30 23:53:16.288201+00	117	213	1	24
168	t	\N	2026-05-30 23:53:16.288206+00	118	215	1	24
169	t	\N	2026-05-30 23:53:16.28821+00	119	217	1	24
170	t	\N	2026-05-30 23:53:16.288214+00	120	219	1	24
171	t	\N	2026-05-30 23:53:16.288219+00	121	221	1	24
172	t	\N	2026-05-30 23:53:16.288223+00	122	223	1	24
173	t	\N	2026-05-30 23:53:16.288227+00	123	225	1	24
174	t	\N	2026-05-30 23:53:16.288232+00	124	227	1	24
175	t	\N	2026-05-30 23:53:16.288236+00	125	229	1	24
176	t	\N	2026-05-30 23:53:16.28824+00	126	231	1	24
177	t	\N	2026-05-30 23:53:16.288245+00	127	233	1	24
178	t	\N	2026-05-30 23:53:16.288249+00	128	235	1	24
179	t	\N	2026-05-30 23:53:16.288254+00	129	238	1	24
180	t	\N	2026-05-30 23:53:16.288258+00	130	239	1	24
181	t	\N	2026-05-30 23:53:16.288263+00	131	241	1	24
182	t	\N	2026-05-30 23:53:16.288267+00	132	243	1	24
183	t	\N	2026-05-30 23:53:16.288272+00	133	245	1	24
184	t	\N	2026-05-30 23:53:16.288276+00	134	247	1	24
185	t	\N	2026-05-30 23:53:16.288281+00	135	249	1	24
186	t	\N	2026-05-30 23:53:16.288285+00	136	252	1	24
187	t	\N	2026-05-30 23:53:16.288289+00	137	254	1	24
188	t	\N	2026-05-30 23:53:16.288294+00	138	255	1	24
189	t	\N	2026-05-30 23:53:16.288298+00	139	257	1	24
190	t	\N	2026-05-30 23:53:16.288303+00	140	259	1	24
191	t	\N	2026-05-30 23:53:16.288308+00	141	261	1	24
192	t	\N	2026-05-30 23:53:16.288312+00	142	263	1	24
193	t	\N	2026-05-30 23:53:16.288317+00	143	265	1	24
194	f	D	2026-05-30 23:53:16.288321+00	144	265	1	24
195	t	\N	2026-05-30 23:53:16.288325+00	145	267	1	24
196	t	\N	2026-05-30 23:53:16.28833+00	146	269	1	24
197	t	\N	2026-05-30 23:53:16.288334+00	147	271	1	24
198	t	\N	2026-05-30 23:53:16.288339+00	148	273	1	24
199	t	\N	2026-05-30 23:53:16.288343+00	149	275	1	24
200	t	\N	2026-05-30 23:53:16.288348+00	150	277	1	24
201	t	\N	2026-05-30 23:53:16.288352+00	151	279	1	24
202	t	\N	2026-05-30 23:53:16.288357+00	152	281	1	24
203	t	\N	2026-05-30 23:53:16.288361+00	153	293	1	24
204	t	\N	2026-05-31 22:56:54.844653+00	1	5	1	25
205	t	\N	2026-05-31 22:56:54.844672+00	2	6	1	25
206	t	\N	2026-05-31 22:56:54.844679+00	3	8	1	25
207	t	\N	2026-05-31 22:56:54.844685+00	4	9	1	25
208	t	\N	2026-05-31 22:56:54.844692+00	5	11	1	25
209	t	\N	2026-05-31 22:56:54.844698+00	6	13	1	25
210	t	\N	2026-05-31 22:56:54.844715+00	7	14	1	25
211	t	\N	2026-05-31 22:56:54.844728+00	8	16	1	25
212	t	\N	2026-05-31 22:56:54.844735+00	9	18	1	25
213	t	\N	2026-05-31 22:56:54.844741+00	10	20	1	25
214	t	\N	2026-05-31 22:56:54.844747+00	11	21	1	25
215	t	\N	2026-05-31 22:56:54.844753+00	12	23	1	25
216	t	\N	2026-05-31 22:56:54.84476+00	13	25	1	25
217	t	\N	2026-05-31 22:56:54.844766+00	14	28	1	25
218	t	\N	2026-05-31 22:56:54.844772+00	15	28	1	25
219	t	\N	2026-05-31 22:56:54.844785+00	16	30	1	25
220	t	\N	2026-05-31 22:56:54.844792+00	17	32	1	25
221	t	\N	2026-05-31 22:56:54.844798+00	18	34	1	25
222	t	\N	2026-05-31 22:56:54.844804+00	19	35	1	25
223	t	\N	2026-05-31 22:56:54.84481+00	20	37	1	25
224	t	\N	2026-05-31 22:56:54.844816+00	21	39	1	25
225	t	\N	2026-05-31 22:56:54.844822+00	22	41	1	25
226	t	\N	2026-05-31 22:56:54.844828+00	23	42	1	25
227	t	\N	2026-05-31 22:56:54.844833+00	24	44	1	25
228	t	\N	2026-05-31 22:56:54.844839+00	25	46	1	25
229	t	\N	2026-05-31 22:56:54.844846+00	26	48	1	25
230	t	\N	2026-05-31 22:56:54.844852+00	27	49	1	25
231	t	\N	2026-05-31 22:56:54.844858+00	28	51	1	25
232	t	\N	2026-05-31 22:56:54.844865+00	29	54	1	25
233	t	\N	2026-05-31 22:56:54.844871+00	30	55	1	25
234	t	\N	2026-05-31 22:56:54.844894+00	31	56	1	25
235	t	\N	2026-05-31 22:56:54.844906+00	32	58	1	25
236	t	\N	2026-05-31 22:56:54.844913+00	33	60	1	25
237	t	\N	2026-05-31 22:56:54.844919+00	34	61	1	25
238	t	\N	2026-05-31 22:56:54.844925+00	35	63	1	25
239	t	\N	2026-05-31 22:56:54.844931+00	36	65	1	25
240	t	\N	2026-05-31 22:56:54.844939+00	37	67	1	25
241	t	\N	2026-05-31 22:56:54.84495+00	38	68	1	25
242	t	\N	2026-05-31 22:56:54.844956+00	39	70	1	25
243	t	\N	2026-05-31 22:56:54.844963+00	40	72	1	25
244	t	\N	2026-05-31 22:56:54.844969+00	41	74	1	25
245	t	\N	2026-05-31 22:56:54.844981+00	42	75	1	25
246	t	\N	2026-05-31 22:56:54.845022+00	43	78	1	25
247	t	\N	2026-05-31 22:56:54.845033+00	44	79	1	25
248	t	\N	2026-05-31 22:56:54.84504+00	45	81	1	25
249	t	\N	2026-05-31 22:56:54.845046+00	46	82	1	25
250	t	\N	2026-05-31 22:56:54.845052+00	47	84	1	25
251	t	\N	2026-05-31 22:56:54.845064+00	48	86	1	25
252	t	\N	2026-05-31 22:56:54.84507+00	49	88	1	25
253	t	\N	2026-05-31 22:56:54.845076+00	50	90	1	25
254	t	\N	2026-05-31 22:56:54.845087+00	51	92	1	25
255	t	\N	2026-05-31 22:56:54.845093+00	52	94	1	25
256	t	\N	2026-05-31 22:56:54.845106+00	53	96	1	25
257	t	\N	2026-05-31 22:56:54.845113+00	54	97	1	25
258	t	\N	2026-05-31 22:56:54.845119+00	55	99	1	25
259	t	\N	2026-05-31 22:56:54.845125+00	56	100	1	25
260	t	\N	2026-05-31 22:56:54.845136+00	57	102	1	25
261	t	\N	2026-05-31 22:56:54.84515+00	58	105	1	25
262	t	\N	2026-05-31 22:56:54.845161+00	59	106	1	25
263	t	\N	2026-05-31 22:56:54.845167+00	60	108	1	25
264	t	\N	2026-05-31 22:56:54.845173+00	61	109	1	25
265	t	\N	2026-05-31 22:56:54.845179+00	62	111	1	25
266	t	\N	2026-05-31 22:56:54.845185+00	63	113	1	25
267	t	\N	2026-05-31 22:56:54.845197+00	64	115	1	25
268	t	\N	2026-05-31 22:56:54.845203+00	65	117	1	25
269	t	\N	2026-05-31 22:56:54.845215+00	66	119	1	25
270	t	\N	2026-05-31 22:56:54.845226+00	67	120	1	25
271	t	\N	2026-05-31 22:56:54.845232+00	68	122	1	25
272	t	\N	2026-05-31 22:56:54.845238+00	69	124	1	25
273	t	\N	2026-05-31 22:56:54.845244+00	70	126	1	25
274	t	\N	2026-05-31 22:56:54.84525+00	71	128	1	25
275	t	\N	2026-05-31 22:56:54.845255+00	72	130	1	25
276	t	\N	2026-05-31 22:56:54.845261+00	73	132	1	25
277	t	\N	2026-05-31 22:56:54.845267+00	74	133	1	25
278	t	\N	2026-05-31 22:56:54.845273+00	75	136	1	25
279	t	\N	2026-05-31 22:56:54.845279+00	76	137	1	25
280	t	\N	2026-05-31 22:56:54.845285+00	77	139	1	25
281	t	\N	2026-05-31 22:56:54.845291+00	78	141	1	25
282	t	\N	2026-05-31 22:56:54.845298+00	79	143	1	25
283	t	\N	2026-05-31 22:56:54.845304+00	80	145	1	25
284	t	\N	2026-05-31 22:56:54.84531+00	81	146	1	25
285	t	\N	2026-05-31 22:56:54.845316+00	82	149	1	25
286	t	\N	2026-05-31 22:56:54.845321+00	83	150	1	25
287	t	\N	2026-05-31 22:56:54.845327+00	84	152	1	25
288	t	\N	2026-05-31 22:56:54.845333+00	85	154	1	25
289	t	\N	2026-05-31 22:56:54.845339+00	86	157	1	25
290	t	\N	2026-05-31 22:56:54.845345+00	87	158	1	25
291	t	\N	2026-05-31 22:56:54.84535+00	88	160	1	25
292	t	\N	2026-05-31 22:56:54.845357+00	89	161	1	25
293	t	\N	2026-05-31 22:56:54.845362+00	90	163	1	25
294	t	\N	2026-05-31 22:56:54.845368+00	91	165	1	25
295	t	\N	2026-05-31 22:56:54.845374+00	92	167	1	25
296	t	\N	2026-05-31 22:56:54.84538+00	93	169	1	25
297	t	\N	2026-05-31 22:56:54.845387+00	94	171	1	25
298	t	\N	2026-05-31 22:56:54.845392+00	95	173	1	25
299	t	\N	2026-05-31 22:56:54.845398+00	96	175	1	25
300	t	\N	2026-05-31 22:56:54.845404+00	97	177	1	25
301	t	\N	2026-05-31 22:56:54.84541+00	98	178	1	25
302	t	\N	2026-05-31 22:56:54.845416+00	99	181	1	25
303	t	\N	2026-05-31 22:56:54.845422+00	100	182	1	25
304	t	\N	2026-05-31 22:56:54.845427+00	101	184	1	25
305	t	\N	2026-05-31 22:56:54.845433+00	102	187	1	25
306	t	\N	2026-05-31 22:56:54.845439+00	103	190	1	25
307	f	D	2026-05-31 22:56:54.845445+00	104	190	1	25
308	t	\N	2026-05-31 22:56:54.845451+00	105	192	1	25
309	t	\N	2026-05-31 22:56:54.845457+00	106	194	1	25
310	t	\N	2026-05-31 22:56:54.845463+00	107	196	1	25
311	t	\N	2026-05-31 22:56:54.845469+00	108	197	1	25
312	f	D	2026-05-31 22:56:54.845475+00	109	198	1	25
313	t	\N	2026-05-31 22:56:54.845481+00	110	200	1	25
314	t	\N	2026-05-31 22:56:54.845487+00	111	203	1	25
315	t	\N	2026-05-31 22:56:54.845493+00	112	205	1	25
316	t	\N	2026-05-31 22:56:54.845498+00	113	206	1	25
317	t	\N	2026-05-31 22:56:54.845504+00	114	208	1	25
318	t	\N	2026-05-31 22:56:54.84551+00	115	210	1	25
319	t	\N	2026-05-31 22:56:54.845516+00	116	211	1	25
320	t	\N	2026-05-31 22:56:54.845522+00	117	213	1	25
321	t	\N	2026-05-31 22:56:54.845528+00	118	215	1	25
322	t	\N	2026-05-31 22:56:54.845534+00	119	217	1	25
323	t	\N	2026-05-31 22:56:54.84554+00	120	219	1	25
324	t	\N	2026-05-31 22:56:54.845546+00	121	221	1	25
325	t	\N	2026-05-31 22:56:54.845559+00	122	223	1	25
326	t	\N	2026-05-31 22:56:54.845565+00	123	225	1	25
327	t	\N	2026-05-31 22:56:54.845571+00	124	227	1	25
328	t	\N	2026-05-31 22:56:54.845577+00	125	229	1	25
329	t	\N	2026-05-31 22:56:54.845603+00	126	231	1	25
330	t	\N	2026-05-31 22:56:54.845625+00	127	233	1	25
331	t	\N	2026-05-31 22:56:54.845632+00	128	235	1	25
332	t	\N	2026-05-31 22:56:54.845638+00	129	238	1	25
333	t	\N	2026-05-31 22:56:54.845644+00	130	239	1	25
334	t	\N	2026-05-31 22:56:54.84565+00	131	241	1	25
335	t	\N	2026-05-31 22:56:54.845655+00	132	243	1	25
336	t	\N	2026-05-31 22:56:54.845661+00	133	245	1	25
337	t	\N	2026-05-31 22:56:54.845667+00	134	247	1	25
338	t	\N	2026-05-31 22:56:54.845673+00	135	249	1	25
339	t	\N	2026-05-31 22:56:54.845678+00	136	252	1	25
340	t	\N	2026-05-31 22:56:54.845704+00	137	254	1	25
341	t	\N	2026-05-31 22:56:54.845724+00	138	255	1	25
342	t	\N	2026-05-31 22:56:54.845751+00	139	257	1	25
343	t	\N	2026-05-31 22:56:54.845778+00	140	259	1	25
344	t	\N	2026-05-31 22:56:54.845804+00	141	261	1	25
345	t	\N	2026-05-31 22:56:54.845817+00	142	263	1	25
346	t	\N	2026-05-31 22:56:54.845828+00	143	265	1	25
347	f	D	2026-05-31 22:56:54.845849+00	144	265	1	25
348	t	\N	2026-05-31 22:56:54.84587+00	145	267	1	25
349	t	\N	2026-05-31 22:56:54.845877+00	146	269	1	25
350	t	\N	2026-05-31 22:56:54.845883+00	147	271	1	25
351	t	\N	2026-05-31 22:56:54.845889+00	148	273	1	25
352	t	\N	2026-05-31 22:56:54.845895+00	149	275	1	25
353	t	\N	2026-05-31 22:56:54.845901+00	150	277	1	25
354	t	\N	2026-05-31 22:56:54.845917+00	151	279	1	25
355	t	\N	2026-05-31 22:56:54.845924+00	152	281	1	25
356	t	\N	2026-05-31 22:56:54.845929+00	153	293	1	25
357	t	\N	2026-06-01 06:33:45.258239+00	1	9	1	26
358	t	\N	2026-06-01 06:33:45.258258+00	2	10	1	26
359	t	\N	2026-06-01 06:33:45.258265+00	3	13	1	26
360	t	\N	2026-06-01 06:33:45.258276+00	4	15	1	26
361	f	D	2026-06-01 06:33:45.258282+00	5	16	1	26
362	f	D	2026-06-01 06:33:45.258287+00	6	18	1	26
363	t	\N	2026-06-01 06:33:45.258292+00	7	21	1	26
364	t	\N	2026-06-01 06:52:29.004937+00	1	9	1	27
365	t	\N	2026-06-01 06:52:29.004956+00	2	10	1	27
366	t	\N	2026-06-01 06:52:29.004962+00	3	13	1	27
367	t	\N	2026-06-01 06:52:29.004993+00	4	15	1	27
368	f	D	2026-06-01 06:52:29.005003+00	5	16	1	27
369	f	D	2026-06-01 06:52:29.005009+00	6	18	1	27
370	t	\N	2026-06-01 06:52:29.005014+00	7	21	1	27
371	t	\N	2026-06-01 07:09:26.380462+00	1	9	1	28
372	t	\N	2026-06-01 07:09:26.380478+00	2	10	1	28
373	t	\N	2026-06-01 07:09:26.380484+00	3	13	1	28
374	t	\N	2026-06-01 07:09:26.380489+00	4	15	1	28
375	f	D	2026-06-01 07:09:26.380494+00	5	16	1	28
376	f	D	2026-06-01 07:09:26.380498+00	6	18	1	28
377	t	\N	2026-06-01 07:09:26.380502+00	7	21	1	28
\.
COPY public.workout_video (id, status, is_deleted, created_at, athlete_id, competition_id, score_id, workout_id, "urlPath") FROM stdin;
d404e236-98e5-42a4-9163-89e36db34fb2	S	f	2026-05-28 07:04:36.471404+00	1	1	18	1	https://www.youtube.com/shorts/oUixw23-59U
70ca7abc-88cf-4ec3-9703-40e7d218fd6a	S	f	2026-05-28 07:21:21.147762+00	1	1	19	1	https://www.youtube.com/shorts/oUixw23-59U
fa49e1c9-235e-479d-a862-781f66c9d468	S	f	2026-05-30 19:16:04.347061+00	1	1	23	1	https://youtube.com/shorts/oUixw23-59U?si=691VaFIgmQOVHB-F
46367d1f-b8e1-4dc5-a02c-040997cb8888	S	f	2026-05-30 19:24:32.155328+00	1	1	24	1	https://www.youtube.com/watch?v=zH8Lfk4jgH4&t=62s
4c3fa728-550a-4b7d-8a01-f74dcfb261d2	S	f	2026-05-31 17:02:15.290795+00	1	1	25	1	https://www.youtube.com/watch?v=zH8Lfk4jgH4&t=62s
72f1bb4f-5fa7-449a-b370-78ab92249a8c	S	f	2026-06-01 06:29:37.814342+00	1	1	26	1	https://www.youtube.com/shorts/H6vpbqtLoA8
bcae9b84-f481-4bc1-96b1-c01f926ac13d	S	f	2026-06-01 06:48:34.197217+00	1	1	27	1	https://www.youtube.com/shorts/H6vpbqtLoA8
d4a8f75a-f725-44ba-bbc2-ecbbeafc7878	S	f	2026-06-01 07:05:41.616156+00	1	1	28	1	https://www.youtube.com/shorts/H6vpbqtLoA8
\.
COPY public.workout_workout (id, name, description, type, total_reps, time_cap, is_active) FROM stdin;
1	Karen	150 wall balls for time	FT	150	600	t
\.
COPY public.workout_workoutcomponent (id, sequence, reps, weight, height, movement_id, workout_id, round) FROM stdin;
1	1	150	20	\N	1	1	1
\.
