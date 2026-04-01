--
-- PostgreSQL database dump
--

\restrict LccE2kmIxV106pYa7SJgrs6b60D74ezqmLISDraVQvLMJ1qH9co8lB0dDM4JHo0

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    id integer NOT NULL,
    module_type character varying(60) NOT NULL,
    farmer_id integer NOT NULL,
    department_id integer NOT NULL,
    season character varying(20) NOT NULL,
    activity_type character varying(150) NOT NULL,
    activity_date date NOT NULL,
    description text,
    remarks text,
    created_by integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT chk_activity_season CHECK (((season)::text = ANY ((ARRAY['Kharif'::character varying, 'Rabi'::character varying])::text[])))
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activities_id_seq OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    module_type character varying(60),
    record_id integer,
    details text,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.departments_id_seq OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: farmers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.farmers (
    id integer NOT NULL,
    farmer_name character varying(150) NOT NULL,
    village character varying(150) NOT NULL,
    contact_number character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.farmers OWNER TO postgres;

--
-- Name: farmers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.farmers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.farmers_id_seq OWNER TO postgres;

--
-- Name: farmers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.farmers_id_seq OWNED BY public.farmers.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reports (
    id integer NOT NULL,
    report_name character varying(200) NOT NULL,
    generated_by integer,
    filter_json text,
    file_path text,
    generated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.reports OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reports_id_seq OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    full_name character varying(150) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT chk_user_role CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'staff'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: activities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities ALTER COLUMN id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: farmers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farmers ALTER COLUMN id SET DEFAULT nextval('public.farmers_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: activities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activities (id, module_type, farmer_id, department_id, season, activity_type, activity_date, description, remarks, created_by, created_at, updated_at) FROM stdin;
3	Visitor Farmers	3	7	Kharif	ju	2026-03-18	uu	dsd	1	2026-03-18 16:34:56.734055	2026-03-18 16:34:56.734062
6	Front Line Demonstrations (FLD)	6	2	Kharif	FLD Entry	2026-03-19	5\t5	ss	1	2026-03-18 18:36:45.483601	2026-03-18 18:36:45.483604
7	Front Line Demonstrations (FLD)	7	7	Kharif	FLD Entry	2026-03-19	fff	dd	1	2026-03-18 18:37:31.23536	2026-03-18 18:37:31.235363
8	On Farm Testing (OFT)	8	1	Kharif	Refinement	2026-03-19	dd	dd	1	2026-03-18 18:43:49.732025	2026-03-18 18:43:49.732031
9	On Farm Testing (OFT)	9	2	Kharif	General OFT	2026-03-19	DD	DD	1	2026-03-18 18:44:13.736841	2026-03-18 18:44:13.736847
10	Visitor Farmers	3	7	Kharif	Consultation	2026-03-18	uu	dsd	1	2026-03-18 18:49:46.248364	2026-03-18 18:49:46.248372
11	Front Line Demonstrations (FLD)	10	1	Kharif	FLD Entry	2026-03-19	dd	ff	1	2026-03-18 18:50:40.992138	2026-03-18 18:50:40.992144
12	On Farm Testing (OFT)	11	7	Kharif	General OFT	2026-03-19	f	ff	1	2026-03-18 18:51:56.297972	2026-03-18 18:51:56.297976
13	On Farm Testing (OFT)	12	1	Rabi	Assessment	2026-03-19			1	2026-03-18 18:52:30.622664	2026-03-18 18:52:30.622668
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, user_id, action, module_type, record_id, details, created_at) FROM stdin;
1	1	create_activity	Front Line Demonstrations (FLD)	1	Created activity for Raj	2026-03-18 16:02:25.142532
2	1	generate_report	Reports	1	Generated report file: d:/kvk/reports/test_export.csv	2026-03-18 16:05:49.627411
3	1	generate_report	Reports	2	Generated report file: d:/kvk/reports/test_export.csv	2026-03-18 16:06:23.27223
4	1	generate_report	Reports	3	Generated report file: D:/kvk/kvk_report_20260318_213923.pdf	2026-03-18 16:09:25.594103
5	1	delete_activity	Front Line Demonstrations (FLD)	1	Deleted activity	2026-03-18 16:11:46.710131
6	1	create_activity	Visitor Farmers	2	Created activity for Raviraj	2026-03-18 16:24:42.498526
7	1	generate_report	Reports	4	Generated report file: D:/kvk/kvk_report_20260318_215454.pdf	2026-03-18 16:24:56.180496
8	1	delete_activity	Visitor Farmers	2	Deleted activity	2026-03-18 16:34:32.751581
9	1	create_activity	Visitor Farmers	3	Created activity for Raj	2026-03-18 16:34:56.808309
10	1	create_activity	Visitor Farmers	4	Created activity for ravi	2026-03-18 18:11:54.652671
11	1	create_activity	Visitor Farmers	5	Created activity for ravi	2026-03-18 18:12:16.736125
12	1	delete_activity	Visitor Farmers	4	Deleted activity	2026-03-18 18:12:26.748523
13	1	backup_database	Backup	\N	Backup generated: D:/kvk/backups\\kvk_backup_20260318_234311.sql	2026-03-18 18:13:12.663124
14	1	backup_database	Backup	\N	Backup generated: D:\\kvk\\backups\\pre_restore\\kvk_backup_20260318_234802.sql	2026-03-18 18:18:02.759357
15	1	generate_report	Reports	6	Generated report file: D:/kvk/kvk_report_20260318_235543.csv	2026-03-18 18:25:45.266454
16	1	deactivate_user	User Management	1	Updated user status	2026-03-18 18:28:12.371137
17	1	activate_user	User Management	1	Updated user status	2026-03-18 18:28:19.347092
18	1	generate_report	Reports	7	Generated report file: D:/kvk/kvk_report_20260318_235837.pdf	2026-03-18 18:28:39.624557
19	1	backup_database	Backup	\N	Backup generated: D:/kvk/backups/pre_restore\\kvk_backup_20260319_000029.sql	2026-03-18 18:30:30.305852
20	1	backup_database	Backup	\N	Backup generated: D:\\kvk\\backups\\pre_restore\\kvk_backup_20260319_000045.sql	2026-03-18 18:30:45.861202
21	1	create_activity	Front Line Demonstrations (FLD)	6	Created activity for Raj	2026-03-18 18:36:45.54901
22	1	create_activity	Front Line Demonstrations (FLD)	7	Created activity for s	2026-03-18 18:37:31.251133
23	1	create_activity	On Farm Testing (OFT)	8	Created activity for raj	2026-03-18 18:43:49.80603
24	1	create_activity	On Farm Testing (OFT)	9	Created activity for rA	2026-03-18 18:44:13.754634
25	1	create_activity	Visitor Farmers	10	Created activity for Raj	2026-03-18 18:49:46.425653
26	1	delete_activity	Visitor Farmers	5	Deleted activity	2026-03-18 18:49:54.352431
27	1	create_activity	Front Line Demonstrations (FLD)	11	Created activity for d	2026-03-18 18:50:41.011086
28	1	create_activity	On Farm Testing (OFT)	12	Created activity for d	2026-03-18 18:51:56.301503
29	1	create_activity	On Farm Testing (OFT)	13	Created activity for dd	2026-03-18 18:52:30.626227
30	1	generate_report	Reports	8	Generated report file: D:/kvk/kvk_report_20260319_002311.pdf	2026-03-18 18:53:13.746922
31	1	generate_report	Reports	9	Generated report file: D:/kvk/kvk_report_20260319_002722.pdf	2026-03-18 18:57:24.41347
32	1	generate_report	Reports	10	Generated report file: C:/Users/ADMIN/Downloads/kvk_report_20260321_142758.pdf	2026-03-21 08:58:05.33501
33	1	generate_report	Reports	11	Generated report file: C:/Users/ADMIN/Downloads/kvk_report_20260321_142809.csv	2026-03-21 08:58:17.587492
34	1	generate_report	Reports	12	Generated report file: D:/kvk/kvk_report_20260329_103128.csv	2026-03-29 05:01:31.753294
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.departments (id, name, created_at) FROM stdin;
1	Agronomy	2026-03-18 15:57:23.769847
2	Horticulture	2026-03-18 15:57:23.769853
3	Plant Protection	2026-03-18 15:57:23.769856
4	Veterinary Science	2026-03-18 15:57:23.769857
5	Soil Science	2026-03-18 15:57:23.769859
6	Home Science	2026-03-18 15:57:23.76986
7	Agricultural Extension	2026-03-18 15:57:23.769862
\.


--
-- Data for Name: farmers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.farmers (id, farmer_name, village, contact_number, created_at, updated_at) FROM stdin;
1	Raj	dhoki	8788117173	2026-03-18 16:02:25.083788	2026-03-18 16:02:25.083793
2	Raviraj	Dhoki	8788117175	2026-03-18 16:24:42.421459	2026-03-18 16:24:42.421467
3	Raj	dho	8788225525	2026-03-18 16:34:56.731142	2026-03-18 16:34:56.731149
4	ravi	f	8788007122	2026-03-18 18:11:54.570413	2026-03-18 18:11:54.570422
5	ravi	dhoki	8788007122	2026-03-18 18:12:16.730838	2026-03-18 18:12:16.730842
6	Raj	Dhoki	8788244643	2026-03-18 18:36:45.481627	2026-03-18 18:36:45.481631
7	s	dd	8711551266	2026-03-18 18:37:31.234355	2026-03-18 18:37:31.234359
8	raj	dhoki	8788117173	2026-03-18 18:43:49.72848	2026-03-18 18:43:49.728488
9	rA	DDS	8588114536	2026-03-18 18:44:13.735348	2026-03-18 18:44:13.735354
10	d	f	8788225453	2026-03-18 18:50:40.990134	2026-03-18 18:50:40.99014
11	d	d	8755441425	2026-03-18 18:51:56.296798	2026-03-18 18:51:56.296801
12	dd	ff	8577224156	2026-03-18 18:52:30.621731	2026-03-18 18:52:30.621734
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reports (id, report_name, generated_by, filter_json, file_path, generated_at) FROM stdin;
1	KVK CSV Report	1	{"start_date": "2026-03-01", "end_date": "2026-03-31", "module_type": "All", "department_id": null}	d:/kvk/reports/test_export.csv	2026-03-18 16:05:49.563448
2	KVK CSV Report	1	{"start_date": "2026-03-01", "end_date": "2026-03-31", "module_type": "All", "department_id": null}	d:/kvk/reports/test_export.csv	2026-03-18 16:06:22.883885
3	KVK Activity Report	1	{"start_date": "2026-02-18", "end_date": "2026-03-19", "department_id": null, "module_type": "All"}	D:/kvk/kvk_report_20260318_213923.pdf	2026-03-18 16:09:25.532649
4	KVK Activity Report	1	{"start_date": "2026-02-18", "end_date": "2026-03-18", "department_id": null, "module_type": "All"}	D:/kvk/kvk_report_20260318_215454.pdf	2026-03-18 16:24:56.163917
5	KVK Activity Report	1	{"start_date": "2026-02-18", "end_date": "2026-03-20", "department_id": null, "module_type": "All"}	D:/kvk/kvk_report_20260318_235517.pdf	2026-03-18 18:25:19.109218
6	KVK CSV Report	1	{"start_date": "2026-02-18", "end_date": "2026-03-20", "department_id": null, "module_type": "All"}	D:/kvk/kvk_report_20260318_235543.csv	2026-03-18 18:25:45.253198
7	KVK Activity Report	1	{"start_date": "2026-02-18", "end_date": "2026-03-18", "department_id": 7, "module_type": "All"}	D:/kvk/kvk_report_20260318_235837.pdf	2026-03-18 18:28:39.567649
8	KVK Activity Report	1	{"start_date": "2026-02-19", "end_date": "2026-03-19", "department_id": null, "module_type": "All"}	D:/kvk/kvk_report_20260319_002311.pdf	2026-03-18 18:53:13.740286
9	KVK Activity Report	1	{"start_date": "2026-02-19", "end_date": "2026-03-19", "department_id": 2, "module_type": "On Farm Testing (OFT)"}	D:/kvk/kvk_report_20260319_002722.pdf	2026-03-18 18:57:24.349874
10	KVK Activity Report	1	{"start_date": "2026-02-21", "end_date": "2026-03-21", "department_id": null, "module_type": "All"}	C:/Users/ADMIN/Downloads/kvk_report_20260321_142758.pdf	2026-03-21 08:58:05.210157
11	KVK CSV Report	1	{"start_date": "2026-02-21", "end_date": "2026-03-21", "department_id": null, "module_type": "All"}	C:/Users/ADMIN/Downloads/kvk_report_20260321_142809.csv	2026-03-21 08:58:17.573298
12	KVK CSV Report	1	{"start_date": "2026-02-28", "end_date": "2026-03-29", "department_id": null, "module_type": "All"}	D:/kvk/kvk_report_20260329_103128.csv	2026-03-29 05:01:31.69038
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, full_name, password_hash, role, is_active, created_at, updated_at) FROM stdin;
1	admin	System Administrator	$pbkdf2-sha256$29000$GKOUsnbOmVMKgbDWWiuFMA$sV4Q4BkloHvnf3DD1qe8d9zPkOmY4zy3sqPMsxDwpDA	admin	t	2026-03-18 15:57:23.825728	2026-03-18 18:28:19.332795
\.


--
-- Name: activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activities_id_seq', 13, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 34, true);


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.departments_id_seq', 7, true);


--
-- Name: farmers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.farmers_id_seq', 12, true);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reports_id_seq', 12, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: departments departments_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_name_key UNIQUE (name);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: farmers farmers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farmers
    ADD CONSTRAINT farmers_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_activities_activity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activities_activity_type ON public.activities USING btree (activity_type);


--
-- Name: idx_activities_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activities_date ON public.activities USING btree (activity_date);


--
-- Name: idx_activities_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activities_department ON public.activities USING btree (department_id);


--
-- Name: idx_activities_module; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activities_module ON public.activities USING btree (module_type);


--
-- Name: idx_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: activities activities_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: activities activities_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: activities activities_farmer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_farmer_id_fkey FOREIGN KEY (farmer_id) REFERENCES public.farmers(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: reports reports_generated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_generated_by_fkey FOREIGN KEY (generated_by) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict LccE2kmIxV106pYa7SJgrs6b60D74ezqmLISDraVQvLMJ1qH9co8lB0dDM4JHo0

