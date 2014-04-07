--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.13
-- Dumped by pg_dump version 9.1.13
-- Started on 2014-04-07 18:30:43 MSK

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 165 (class 3079 OID 11678)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 1915 (class 0 OID 0)
-- Dependencies: 165
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 164 (class 1259 OID 41165)
-- Dependencies: 5
-- Name: states; Type: TABLE; Schema: public; Owner: pgadmin; Tablespace: 
--

CREATE TABLE states (
    id integer NOT NULL,
    user_id integer,
    host character varying(50),
    status integer,
    users bytea
);


ALTER TABLE public.states OWNER TO pgadmin;

--
-- TOC entry 163 (class 1259 OID 41163)
-- Dependencies: 164 5
-- Name: states_id_seq; Type: SEQUENCE; Schema: public; Owner: pgadmin
--

CREATE SEQUENCE states_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.states_id_seq OWNER TO pgadmin;

--
-- TOC entry 1916 (class 0 OID 0)
-- Dependencies: 163
-- Name: states_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgadmin
--

ALTER SEQUENCE states_id_seq OWNED BY states.id;


--
-- TOC entry 162 (class 1259 OID 41155)
-- Dependencies: 5
-- Name: users; Type: TABLE; Schema: public; Owner: pgadmin; Tablespace: 
--

CREATE TABLE users (
    id integer NOT NULL,
    username character varying(50),
    password character varying(50)
);


ALTER TABLE public.users OWNER TO pgadmin;

--
-- TOC entry 161 (class 1259 OID 41153)
-- Dependencies: 5 162
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: pgadmin
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO pgadmin;

--
-- TOC entry 1917 (class 0 OID 0)
-- Dependencies: 161
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pgadmin
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- TOC entry 1793 (class 2604 OID 41168)
-- Dependencies: 164 163 164
-- Name: id; Type: DEFAULT; Schema: public; Owner: pgadmin
--

ALTER TABLE ONLY states ALTER COLUMN id SET DEFAULT nextval('states_id_seq'::regclass);


--
-- TOC entry 1792 (class 2604 OID 41158)
-- Dependencies: 162 161 162
-- Name: id; Type: DEFAULT; Schema: public; Owner: pgadmin
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- TOC entry 1907 (class 0 OID 41165)
-- Dependencies: 164 1908
-- Data for Name: states; Type: TABLE DATA; Schema: public; Owner: pgadmin
--

COPY states (id, user_id, host, status, users) FROM stdin;
3	3	127.0.0.1	3	\\x80025d71012e
1	1	127.0.0.1	1	\\x80025d71012e
2	2	127.0.0.1	1	\\x80025d71012e
\.


--
-- TOC entry 1918 (class 0 OID 0)
-- Dependencies: 163
-- Name: states_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgadmin
--

SELECT pg_catalog.setval('states_id_seq', 3, true);


--
-- TOC entry 1905 (class 0 OID 41155)
-- Dependencies: 162 1908
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: pgadmin
--

COPY users (id, username, password) FROM stdin;
1	qwerty	123456
2	qwerty1	123456
3	qwerty2	123456
\.


--
-- TOC entry 1919 (class 0 OID 0)
-- Dependencies: 161
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pgadmin
--

SELECT pg_catalog.setval('users_id_seq', 1, false);


--
-- TOC entry 1799 (class 2606 OID 41173)
-- Dependencies: 164 164 1909
-- Name: states_pkey; Type: CONSTRAINT; Schema: public; Owner: pgadmin; Tablespace: 
--

ALTER TABLE ONLY states
    ADD CONSTRAINT states_pkey PRIMARY KEY (id);


--
-- TOC entry 1801 (class 2606 OID 41175)
-- Dependencies: 164 164 1909
-- Name: states_user_id_key; Type: CONSTRAINT; Schema: public; Owner: pgadmin; Tablespace: 
--

ALTER TABLE ONLY states
    ADD CONSTRAINT states_user_id_key UNIQUE (user_id);


--
-- TOC entry 1795 (class 2606 OID 41160)
-- Dependencies: 162 162 1909
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: pgadmin; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 1797 (class 2606 OID 41162)
-- Dependencies: 162 162 1909
-- Name: users_username_key; Type: CONSTRAINT; Schema: public; Owner: pgadmin; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 1802 (class 2606 OID 41176)
-- Dependencies: 1794 164 162 1909
-- Name: states_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pgadmin
--

ALTER TABLE ONLY states
    ADD CONSTRAINT states_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- TOC entry 1914 (class 0 OID 0)
-- Dependencies: 5
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2014-04-07 18:30:43 MSK

--
-- PostgreSQL database dump complete
--

