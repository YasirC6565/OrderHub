--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-11-12 11:08:06

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
-- TOC entry 224 (class 1259 OID 41237)
-- Name: client_phone_numbers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_phone_numbers (
    id integer NOT NULL,
    client_id integer NOT NULL,
    phone_number text NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 41236)
-- Name: client_phone_numbers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.client_phone_numbers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4836 (class 0 OID 0)
-- Dependencies: 223
-- Name: client_phone_numbers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.client_phone_numbers_id_seq OWNED BY public.client_phone_numbers.id;


--
-- TOC entry 222 (class 1259 OID 41227)
-- Name: clients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clients (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- TOC entry 221 (class 1259 OID 41226)
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4837 (class 0 OID 0)
-- Dependencies: 221
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- TOC entry 218 (class 1259 OID 41190)
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name text NOT NULL,
    unit_synonyms text[] NOT NULL
);


--
-- TOC entry 217 (class 1259 OID 41189)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4838 (class 0 OID 0)
-- Dependencies: 217
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 220 (class 1259 OID 41203)
-- Name: restaurants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.restaurants (
    id integer NOT NULL,
    name text NOT NULL,
    phone_number text
);


--
-- TOC entry 219 (class 1259 OID 41202)
-- Name: restaurants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.restaurants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4839 (class 0 OID 0)
-- Dependencies: 219
-- Name: restaurants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.restaurants_id_seq OWNED BY public.restaurants.id;


--
-- TOC entry 4660 (class 2604 OID 41240)
-- Name: client_phone_numbers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_phone_numbers ALTER COLUMN id SET DEFAULT nextval('public.client_phone_numbers_id_seq'::regclass);


--
-- TOC entry 4659 (class 2604 OID 41230)
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- TOC entry 4657 (class 2604 OID 41193)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 4658 (class 2604 OID 41206)
-- Name: restaurants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurants ALTER COLUMN id SET DEFAULT nextval('public.restaurants_id_seq'::regclass);


--
-- TOC entry 4830 (class 0 OID 41237)
-- Dependencies: 224
-- Data for Name: client_phone_numbers; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.client_phone_numbers VALUES (1, 1, '+447943897718');
INSERT INTO public.client_phone_numbers VALUES (4, 2, '+447951820569');


--
-- TOC entry 4828 (class 0 OID 41227)
-- Dependencies: 222
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.clients VALUES (1, 'Spice Merchant');
INSERT INTO public.clients VALUES (2, 'My Test Restaurant');


--
-- TOC entry 4824 (class 0 OID 41190)
-- Dependencies: 218
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.products VALUES (25, 'Ada Labu', '{box,kg}');
INSERT INTO public.products VALUES (26, 'Ado/Muki', '{box,kg}');
INSERT INTO public.products VALUES (27, 'African Naga', '{box,kg}');
INSERT INTO public.products VALUES (28, 'Almond powder', '{box,kg}');
INSERT INTO public.products VALUES (29, 'Amla', '{box,kg}');
INSERT INTO public.products VALUES (30, 'Apple Custard', '{box,kg,pieces}');
INSERT INTO public.products VALUES (31, 'Apple GALA', '{box}');
INSERT INTO public.products VALUES (32, 'Apple Grannysmith', '{box,pieces}');
INSERT INTO public.products VALUES (33, 'Apple red', '{box,kg,pieces}');
INSERT INTO public.products VALUES (34, 'Asparagus', '{box,pieces}');
INSERT INTO public.products VALUES (35, 'Aubargine', '{box,kg,pieces}');
INSERT INTO public.products VALUES (37, 'Baba Zorda', '{box,pieces}');
INSERT INTO public.products VALUES (38, 'baby chicken', '{box,kg,pieces}');
INSERT INTO public.products VALUES (39, 'Baby Corn', '{box,pieces}');
INSERT INTO public.products VALUES (40, 'Baby Jam', '{box,kg,pieces}');
INSERT INTO public.products VALUES (41, 'Badsha Rice', '{bag}');
INSERT INTO public.products VALUES (42, 'Banana', '{box,pieces}');
INSERT INTO public.products VALUES (43, 'Banana Leaf', '{box,kg,pieces}');
INSERT INTO public.products VALUES (44, 'Banana Shallot', '{bag,kg}');
INSERT INTO public.products VALUES (45, 'Bangladeshi Biscuit', '{box,pieces}');
INSERT INTO public.products VALUES (46, 'Basil', '{box,pieces}');
INSERT INTO public.products VALUES (47, 'Basil Green', '{box,pieces}');
INSERT INTO public.products VALUES (48, 'Bay Leaf', '{box,pieces}');
INSERT INTO public.products VALUES (49, 'Bean Sprouts', '{bag}');
INSERT INTO public.products VALUES (50, 'Beetroot', '{bag,kg,pieces}');
INSERT INTO public.products VALUES (51, 'Beetroot cooked', '{box,pieces}');
INSERT INTO public.products VALUES (52, 'Bindi', '{box,kg}');
INSERT INTO public.products VALUES (53, 'Bindi Frozen', '{box,kg,pieces}');
INSERT INTO public.products VALUES (54, 'Bionda Lettuce', '{box,pieces}');
INSERT INTO public.products VALUES (55, 'Biscuit', '{pieces,tray}');
INSERT INTO public.products VALUES (56, 'Blackberry', '{box,pieces}');
INSERT INTO public.products VALUES (57, 'Blackcurrent', '{box,pieces}');
INSERT INTO public.products VALUES (58, 'Boroi', '{box,kg,pieces}');
INSERT INTO public.products VALUES (59, 'Broad Bean', '{box}');
INSERT INTO public.products VALUES (60, 'Brocoli', '{box,pieces}');
INSERT INTO public.products VALUES (61, 'Brocoli Baby', '{box,kg}');
INSERT INTO public.products VALUES (62, 'Brocoli Stem', '{box,kg,pieces}');
INSERT INTO public.products VALUES (63, 'Brussel Sprouts', '{bag,kg}');
INSERT INTO public.products VALUES (64, 'Bubi', '{box,kg,pieces}');
INSERT INTO public.products VALUES (65, 'Butter Nut Squash', '{box,pieces}');
INSERT INTO public.products VALUES (66, 'Cabbage', '{bag,pieces}');
INSERT INTO public.products VALUES (67, 'Cabbage (Sweetheart)', '{bag,pieces}');
INSERT INTO public.products VALUES (68, 'Cabbage Chinese', '{box,pieces}');
INSERT INTO public.products VALUES (69, 'Cabbage Red', '{bag,pieces}');
INSERT INTO public.products VALUES (70, 'Cabbage Small', '{bag}');
INSERT INTO public.products VALUES (71, 'Cabbage suvoy', '{bag,pieces}');
INSERT INTO public.products VALUES (72, 'Cabbage White', '{bag,pieces}');
INSERT INTO public.products VALUES (73, 'Cabbage(Turkish)', '{box,pieces}');
INSERT INTO public.products VALUES (74, 'Cabbiege Itallian', '{box,pieces}');
INSERT INTO public.products VALUES (75, 'Carnation Milk', '{box,pieces}');
INSERT INTO public.products VALUES (76, 'Carrier Bag', '{box}');
INSERT INTO public.products VALUES (77, 'Carrot', '{bag,kg}');
INSERT INTO public.products VALUES (78, 'Carrot Baby', '{box,kg,pieces}');
INSERT INTO public.products VALUES (79, 'Carrot Donky', '{box,kg}');
INSERT INTO public.products VALUES (80, 'Carrot Net', '{bag,kg}');
INSERT INTO public.products VALUES (81, 'Casava', '{box,kg,pieces}');
INSERT INTO public.products VALUES (82, 'Cauliflower', '{box,pieces}');
INSERT INTO public.products VALUES (83, 'Cauliflower Baby', '{box,pieces}');
INSERT INTO public.products VALUES (84, 'Celery', '{box,pieces}');
INSERT INTO public.products VALUES (85, 'Chapati', '{box,pieces}');
INSERT INTO public.products VALUES (86, 'Cherry', '{box}');
INSERT INTO public.products VALUES (87, 'Cherry Plub', '{box,kg}');
INSERT INTO public.products VALUES (88, 'chicken', '{box,kg,pieces}');
INSERT INTO public.products VALUES (89, 'Chilli Mayo Souse', '{box,pieces}');
INSERT INTO public.products VALUES (90, 'Chilli Powder 5kg', '{bag}');
INSERT INTO public.products VALUES (91, 'Chinese Apple', '{box,kg}');
INSERT INTO public.products VALUES (92, 'Chinese leaves', '{pieces}');
INSERT INTO public.products VALUES (93, 'Chinese Leaves', '{box}');
INSERT INTO public.products VALUES (94, 'Chives', '{box,pieces}');
INSERT INTO public.products VALUES (95, 'chopped onion', '{bag,kg}');
INSERT INTO public.products VALUES (96, 'chopped tomato', '{box}');
INSERT INTO public.products VALUES (97, 'Chopped Tomato', '{pieces}');
INSERT INTO public.products VALUES (98, 'Chow Chow', '{box,pieces}');
INSERT INTO public.products VALUES (99, 'Choy Sum', '{box,pieces}');
INSERT INTO public.products VALUES (100, 'Chun', '{box,pieces}');
INSERT INTO public.products VALUES (101, 'Chutney Cup', '{box,kg,pieces}');
INSERT INTO public.products VALUES (102, 'Chutney Mango', '{box,pieces}');
INSERT INTO public.products VALUES (103, 'Coconut', '{bag,box,pieces}');
INSERT INTO public.products VALUES (104, 'Coconut powder', '{box,kg}');
INSERT INTO public.products VALUES (105, 'Coriander', '{box,pieces}');
INSERT INTO public.products VALUES (106, 'Coriander Khushboo', '{box,pieces}');
INSERT INTO public.products VALUES (107, 'Cos lettuce', '{box,pieces}');
INSERT INTO public.products VALUES (108, 'Courgettes', '{box,kg,pieces}');
INSERT INTO public.products VALUES (109, 'Courgettes Yellow', '{box,kg,pieces}');
INSERT INTO public.products VALUES (110, 'Cucumber', '{box,pieces}');
INSERT INTO public.products VALUES (111, 'Cucumber Baby', '{box,kg,pieces}');
INSERT INTO public.products VALUES (112, 'Curly Kale', '{box}');
INSERT INTO public.products VALUES (113, 'Curry Leaf', '{box,pieces}');
INSERT INTO public.products VALUES (114, 'Data Sag', '{box}');
INSERT INTO public.products VALUES (115, 'Dates', '{box,pieces}');
INSERT INTO public.products VALUES (116, 'Deggi Mirch', '{box,pieces}');
INSERT INTO public.products VALUES (117, 'Diet Coke', '{box,pieces}');
INSERT INTO public.products VALUES (118, 'Dill Leaf', '{box,pieces}');
INSERT INTO public.products VALUES (119, 'Drum Stick', '{box,kg,pieces}');
INSERT INTO public.products VALUES (120, 'Duck', '{box,kg,pieces}');
INSERT INTO public.products VALUES (121, 'Dudhi', '{box,kg,pieces}');
INSERT INTO public.products VALUES (122, 'Egg', '{box,pieces}');
INSERT INTO public.products VALUES (123, 'Egg Large', '{box,pieces}');
INSERT INTO public.products VALUES (124, 'Fine Beans', '{box}');
INSERT INTO public.products VALUES (125, 'Fish', '{pieces}');
INSERT INTO public.products VALUES (126, 'Flat Beans', '{box,kg}');
INSERT INTO public.products VALUES (127, 'flour', '{box,kg,pieces}');
INSERT INTO public.products VALUES (128, 'Flower', '{box,bunch,pieces}');
INSERT INTO public.products VALUES (129, 'Frying Pan', '{box,pieces}');
INSERT INTO public.products VALUES (130, 'G.Pumpkin', '{bag,pieces}');
INSERT INTO public.products VALUES (131, 'Gala Melon', '{box,pieces}');
INSERT INTO public.products VALUES (132, 'Galangal', '{box,kg,pieces}');
INSERT INTO public.products VALUES (133, 'Garlic', '{box,kg}');
INSERT INTO public.products VALUES (134, 'Garlic (Chinese)', '{box}');
INSERT INTO public.products VALUES (135, 'Garlic + Ginger Paste', '{box,kg,pieces}');
INSERT INTO public.products VALUES (136, 'Garlic Paste', '{box,kg,pieces}');
INSERT INTO public.products VALUES (137, 'Garlic Peeled', '{box,kg}');
INSERT INTO public.products VALUES (138, 'Garlic Pre-Packed x 20', '{box,kg,pieces}');
INSERT INTO public.products VALUES (139, 'Ghee', '{box,pieces}');
INSERT INTO public.products VALUES (140, 'Ghee khanam', '{kg}');
INSERT INTO public.products VALUES (141, 'Ghee vegetable', '{bucket}');
INSERT INTO public.products VALUES (142, 'Ginger', '{box,kg}');
INSERT INTO public.products VALUES (143, 'Ginger Paste', '{box,kg,pieces}');
INSERT INTO public.products VALUES (144, 'Gram Flouer', '{bag,pieces}');
INSERT INTO public.products VALUES (145, 'Grapes BLACK', '{box}');
INSERT INTO public.products VALUES (146, 'Grapes red', '{box,pieces}');
INSERT INTO public.products VALUES (147, 'Grapes white', '{box,pieces}');
INSERT INTO public.products VALUES (148, 'Grappes red', '{box}');
INSERT INTO public.products VALUES (149, 'Green Apple', '{box,kg,pieces}');
INSERT INTO public.products VALUES (150, 'Green Bullet Chilli', '{box,kg}');
INSERT INTO public.products VALUES (151, 'Green Chilli', '{box,kg}');
INSERT INTO public.products VALUES (152, 'Green Leaf', '{box}');
INSERT INTO public.products VALUES (153, 'Green Lolo', '{box,kg,pieces}');
INSERT INTO public.products VALUES (154, 'Green Plantain', '{box,kg,pieces}');
INSERT INTO public.products VALUES (155, 'Guava', '{box,pieces}');
INSERT INTO public.products VALUES (156, 'Gulab Jamun', '{pieces}');
INSERT INTO public.products VALUES (157, 'Gur', '{box,kg,pieces}');
INSERT INTO public.products VALUES (158, 'hakimpuri', '{box,pieces}');
INSERT INTO public.products VALUES (159, 'Haldi Powder 5kg', '{bag}');
INSERT INTO public.products VALUES (160, 'Haldi Raw', '{box,kg}');
INSERT INTO public.products VALUES (161, 'Holi Basil', '{box,pieces}');
INSERT INTO public.products VALUES (162, 'Holly Basil', '{box,pieces}');
INSERT INTO public.products VALUES (163, 'Iceberg Lettuce', '{box,pieces}');
INSERT INTO public.products VALUES (164, 'Jalapeno', '{box,kg}');
INSERT INTO public.products VALUES (165, 'Jali', '{box,pieces}');
INSERT INTO public.products VALUES (166, 'Jally Nut', '{box,pieces}');
INSERT INTO public.products VALUES (167, 'Jamir Ada', '{box,pieces}');
INSERT INTO public.products VALUES (168, 'JELABI', '{box,kg}');
INSERT INTO public.products VALUES (169, 'Jelly Nut (Coconut)', '{bag,pieces}');
INSERT INTO public.products VALUES (170, 'Jolpai', '{box,kg}');
INSERT INTO public.products VALUES (171, 'Kadu', '{box,kg,pieces}');
INSERT INTO public.products VALUES (172, 'Kadu/Jaali Box NO 306 Kadu/Jaali Pieces NO 307 Kadu/Jaali Kg NO 308 Kai Choi', '{box}');
INSERT INTO public.products VALUES (173, 'kakrull', '{box,kg}');
INSERT INTO public.products VALUES (174, 'Kala Chana', '{box,kg,pieces}');
INSERT INTO public.products VALUES (175, 'Kala Jam', '{box,pieces}');
INSERT INTO public.products VALUES (176, 'Karela', '{box,kg}');
INSERT INTO public.products VALUES (177, 'Kashmiri Paste', '{box,kg,pieces}');
INSERT INTO public.products VALUES (178, 'Kasturi Methi', '{bag}');
INSERT INTO public.products VALUES (179, 'Katal', '{box,pieces}');
INSERT INTO public.products VALUES (180, 'Katal Bisi', '{box}');
INSERT INTO public.products VALUES (181, 'Kebab', '{box,kg,pieces}');
INSERT INTO public.products VALUES (182, 'Kema', '{box,kg}');
INSERT INTO public.products VALUES (183, 'King Prawn 6/8', '{box,kg,pieces}');
INSERT INTO public.products VALUES (184, 'Kitchen King', '{box,pieces}');
INSERT INTO public.products VALUES (185, 'Kiwi', '{box,pieces}');
INSERT INTO public.products VALUES (186, 'Kochu', '{box,bunch}');
INSERT INTO public.products VALUES (187, 'Kohi', '{box,kg}');
INSERT INTO public.products VALUES (188, 'Komla', '{box,kg,pieces}');
INSERT INTO public.products VALUES (189, 'Kra Chai', '{box,pieces}');
INSERT INTO public.products VALUES (190, 'Kuhi', '{box,kg}');
INSERT INTO public.products VALUES (191, 'Labu', '{box,pieces}');
INSERT INTO public.products VALUES (192, 'Lal Sag', '{box,pieces}');
INSERT INTO public.products VALUES (193, 'leek', '{pieces}');
INSERT INTO public.products VALUES (194, 'Leek', '{bag}');
INSERT INTO public.products VALUES (195, 'Lemon', '{box,pieces}');
INSERT INTO public.products VALUES (196, 'Lemon grass', '{box}');
INSERT INTO public.products VALUES (197, 'Lemon Grass', '{pieces}');
INSERT INTO public.products VALUES (198, 'lichi', '{box}');
INSERT INTO public.products VALUES (199, 'Lime', '{box,pieces}');
INSERT INTO public.products VALUES (200, 'Lime Leaf', '{box,pieces}');
INSERT INTO public.products VALUES (201, 'Lime Leave', '{box,pieces}');
INSERT INTO public.products VALUES (202, 'Lime Pickle', '{box,pieces}');
INSERT INTO public.products VALUES (203, 'Long beans', '{box,kg}');
INSERT INTO public.products VALUES (204, 'Long Aubargine(Bangladeshi)', '{box,kg,pieces}');
INSERT INTO public.products VALUES (205, 'Long Baby Aubargine', '{box,kg,pieces}');
INSERT INTO public.products VALUES (206, 'Long Green Chilli', '{box}');
INSERT INTO public.products VALUES (207, 'Long green chilli', '{kg}');
INSERT INTO public.products VALUES (208, 'Long red chilli', '{box,kg,pieces}');
INSERT INTO public.products VALUES (209, 'Lotha', '{box,kg}');
INSERT INTO public.products VALUES (210, 'Lotia Shutki', '{bag,kg,pieces}');
INSERT INTO public.products VALUES (211, 'Lotus Root', '{box,kg}');
INSERT INTO public.products VALUES (212, 'Mandarin', '{box,pieces}');
INSERT INTO public.products VALUES (213, 'Mango', '{box,kg,pieces}');
INSERT INTO public.products VALUES (214, 'Mango Alphonso', '{box}');
INSERT INTO public.products VALUES (215, 'Mango Brazilian', '{box}');
INSERT INTO public.products VALUES (216, 'Mango Chaunsa', '{box}');
INSERT INTO public.products VALUES (217, 'Mango Kesar', '{box}');
INSERT INTO public.products VALUES (218, 'Mango Langra', '{box}');
INSERT INTO public.products VALUES (219, 'Mango Pakistani', '{box}');
INSERT INTO public.products VALUES (220, 'Mango Pulp', '{box,pieces}');
INSERT INTO public.products VALUES (221, 'Mango row', '{box,kg,pieces}');
INSERT INTO public.products VALUES (222, 'Mango sliced', '{box,pieces}');
INSERT INTO public.products VALUES (223, 'Marrow', '{box,pieces}');
INSERT INTO public.products VALUES (224, 'Mathi', '{box,pieces}');
INSERT INTO public.products VALUES (225, 'Meat + Veg Masala', '{box,kg,pieces}');
INSERT INTO public.products VALUES (226, 'Medjool', '{box,kg}');
INSERT INTO public.products VALUES (227, 'melon Box NO 415 melon Pieces NO 416 Melon Cantaloupe', '{box}');
INSERT INTO public.products VALUES (228, 'Melon Cantaloupe', '{pieces}');
INSERT INTO public.products VALUES (229, 'Mic', '{box,pieces}');
INSERT INTO public.products VALUES (230, 'Micro Lemon Balm', '{box,pieces}');
INSERT INTO public.products VALUES (231, 'Micro-Herbs CORIANDER', '{box,pieces}');
INSERT INTO public.products VALUES (232, 'Micro-Herbs MIX', '{box,pieces}');
INSERT INTO public.products VALUES (233, 'Micro-Herbs ONION', '{box,pieces}');
INSERT INTO public.products VALUES (234, 'Micro-Herbs PURPLE', '{box,pieces}');
INSERT INTO public.products VALUES (235, 'Milk', '{box,pieces}');
INSERT INTO public.products VALUES (237, 'Mint Leaf Bunch NO 434 Mint Leaf', '{pieces}');
INSERT INTO public.products VALUES (238, 'Mishti Doi', '{bucket}');
INSERT INTO public.products VALUES (240, 'mix flour', '{box}');
INSERT INTO public.products VALUES (241, 'Mix Leaves', '{box}');
INSERT INTO public.products VALUES (242, 'mix pickle', '{box,pieces}');
INSERT INTO public.products VALUES (243, 'Mix Salad', '{box}');
INSERT INTO public.products VALUES (244, 'Mix vegetable frozen', '{box,pieces}');
INSERT INTO public.products VALUES (245, 'Molasses', '{box,pieces}');
INSERT INTO public.products VALUES (246, 'Momo Zorda', '{box,kg,pieces}');
INSERT INTO public.products VALUES (247, 'Monustu', '{box}');
INSERT INTO public.products VALUES (248, 'Mr Naga', '{box,pieces}');
INSERT INTO public.products VALUES (249, 'Mr Prawn', '{box,pieces}');
INSERT INTO public.products VALUES (250, 'MT samosa', '{bag,pieces}');
INSERT INTO public.products VALUES (251, 'muki', '{box,kg}');
INSERT INTO public.products VALUES (252, 'Mulaa', '{box,pieces}');
INSERT INTO public.products VALUES (253, 'Mushroom Button', '{box}');
INSERT INTO public.products VALUES (254, 'Mushroom Chestnut', '{box}');
INSERT INTO public.products VALUES (255, 'Mushroom Cup', '{box}');
INSERT INTO public.products VALUES (256, 'Mushroom Enoki', '{box,pieces}');
INSERT INTO public.products VALUES (257, 'Mushroom Flat', '{box,pieces}');
INSERT INTO public.products VALUES (258, 'Mushroom Oyster', '{box}');
INSERT INTO public.products VALUES (259, 'Mushroom Wild', '{box,pieces}');
INSERT INTO public.products VALUES (260, 'Mustard cress', '{box,pieces}');
INSERT INTO public.products VALUES (261, 'N.H.P RED', '{box}');
INSERT INTO public.products VALUES (262, 'Naali Saag', '{box,bunch,pieces}');
INSERT INTO public.products VALUES (263, 'Naan Atta', '{bag,kg}');
INSERT INTO public.products VALUES (264, 'Naga', '{box,kg,pieces}');
INSERT INTO public.products VALUES (265, 'Nali Sag', '{box,kg,pieces}');
INSERT INTO public.products VALUES (266, 'Oil K.T.C 20 lt', '{box}');
INSERT INTO public.products VALUES (267, 'Ong Choy', '{box,pieces}');
INSERT INTO public.products VALUES (268, 'Onion', '{bag}');
INSERT INTO public.products VALUES (269, 'Onion 10kg', '{bag}');
INSERT INTO public.products VALUES (270, 'Onion 5kg', '{bag}');
INSERT INTO public.products VALUES (271, 'Onion 60/40', '{bag}');
INSERT INTO public.products VALUES (272, 'Onion Bombay', '{bag,kg,pieces}');
INSERT INTO public.products VALUES (273, 'Onion Catering', '{bag}');
INSERT INTO public.products VALUES (274, 'Onion Chinese', '{bag}');
INSERT INTO public.products VALUES (275, 'Onion coctain', '{bag,kg}');
INSERT INTO public.products VALUES (276, 'Onion Large', '{bag}');
INSERT INTO public.products VALUES (277, 'Onion new crop', '{bag}');
INSERT INTO public.products VALUES (278, 'onion red', '{bag,kg,pieces}');
INSERT INTO public.products VALUES (279, 'Onion Red Large', '{bag,kg}');
INSERT INTO public.products VALUES (280, 'Onion Sliced', '{bag,kg}');
INSERT INTO public.products VALUES (281, 'Onion Spanish 20Kg', '{bag}');
INSERT INTO public.products VALUES (282, 'Onion Spring', '{box,pieces}');
INSERT INTO public.products VALUES (283, 'Orange', '{box,pieces}');
INSERT INTO public.products VALUES (284, 'Orange Blood', '{box,pieces}');
INSERT INTO public.products VALUES (285, 'Orange Colour', '{pieces}');
INSERT INTO public.products VALUES (286, 'Orange jucing', '{box,pieces}');
INSERT INTO public.products VALUES (287, 'Oregano', '{box,bunch}');
INSERT INTO public.products VALUES (288, 'oyster king', '{box,pieces}');
INSERT INTO public.products VALUES (289, 'Pak Choi', '{box,pieces}');
INSERT INTO public.products VALUES (290, 'Pan', '{box,kg,pieces}');
INSERT INTO public.products VALUES (291, 'Paneer', '{box}');
INSERT INTO public.products VALUES (292, 'Paneer (5kg)', '{box}');
INSERT INTO public.products VALUES (293, 'papadam', '{box}');
INSERT INTO public.products VALUES (294, 'Papadam', '{kg,pieces}');
INSERT INTO public.products VALUES (295, 'Papaya', '{box,pieces}');
INSERT INTO public.products VALUES (296, 'Papaya Green', '{box,kg,pieces}');
INSERT INTO public.products VALUES (297, 'Papaya red', '{box,pieces}');
INSERT INTO public.products VALUES (298, 'Papaya YELLOW', '{box}');
INSERT INTO public.products VALUES (299, 'Paper Romano green', '{box,pieces}');
INSERT INTO public.products VALUES (300, 'Paper Romano red', '{box,pieces}');
INSERT INTO public.products VALUES (301, 'Paper(mix cap)', '{box}');
INSERT INTO public.products VALUES (302, 'Parsley CURLY', '{box,pieces}');
INSERT INTO public.products VALUES (303, 'Parsley Flat', '{box,pieces}');
INSERT INTO public.products VALUES (304, 'Parsnip', '{box,kg}');
INSERT INTO public.products VALUES (305, 'Passion Fruits', '{box,pieces}');
INSERT INTO public.products VALUES (306, 'Pathra', '{box,pieces}');
INSERT INTO public.products VALUES (307, 'Pea shoots', '{box,pieces}');
INSERT INTO public.products VALUES (308, 'Peach', '{box}');
INSERT INTO public.products VALUES (309, 'Pear', '{box,kg,pieces}');
INSERT INTO public.products VALUES (310, 'Peeled Tomato', '{box,pieces}');
INSERT INTO public.products VALUES (311, 'Pepper (Green + Red) Large', '{box,kg,pieces}');
INSERT INTO public.products VALUES (312, 'Pepper (Green+Red)', '{box}');
INSERT INTO public.products VALUES (313, 'Pepper (R+Y)', '{box}');
INSERT INTO public.products VALUES (314, 'Pepper Green', '{box,pieces}');
INSERT INTO public.products VALUES (315, 'Pepper Green Large', '{box,kg,pieces}');
INSERT INTO public.products VALUES (316, 'Pepper Red', '{box,pieces}');
INSERT INTO public.products VALUES (317, 'Pepper Red Large', '{box,kg,pieces}');
INSERT INTO public.products VALUES (318, 'Pepper Yellow', '{box,pieces}');
INSERT INTO public.products VALUES (319, 'Physalis', '{box,pieces}');
INSERT INTO public.products VALUES (320, 'Pineapple', '{box,pieces}');
INSERT INTO public.products VALUES (321, 'Pink Ravaia', '{box,kg}');
INSERT INTO public.products VALUES (322, 'Plantain', '{box,kg,pieces}');
INSERT INTO public.products VALUES (323, 'Plum', '{box,pieces}');
INSERT INTO public.products VALUES (324, 'Plum Cherry Tomato', '{box,pieces}');
INSERT INTO public.products VALUES (325, 'Poi Saag', '{box,kg,pieces}');
INSERT INTO public.products VALUES (326, 'Pomi granit', '{box,pieces}');
INSERT INTO public.products VALUES (327, 'Portobello Mushroom', '{box,kg}');
INSERT INTO public.products VALUES (328, 'Potato 4 kg', '{bag}');
INSERT INTO public.products VALUES (329, 'Potato 5kg', '{bag}');
INSERT INTO public.products VALUES (330, 'Potato BABY', '{box,kg}');
INSERT INTO public.products VALUES (331, 'Potato Cyprus', '{bag}');
INSERT INTO public.products VALUES (332, 'Potato HTP Red', '{bag}');
INSERT INTO public.products VALUES (333, 'Potato HTP White', '{bag}');
INSERT INTO public.products VALUES (334, 'Potato Jacket', '{bag,pieces}');
INSERT INTO public.products VALUES (335, 'Potato J-D', '{bag}');
INSERT INTO public.products VALUES (336, 'Potato jumbo', '{bag}');
INSERT INTO public.products VALUES (337, 'Potato King Edward', '{bag,kg}');
INSERT INTO public.products VALUES (338, 'Potato NSD', '{box,kg,pieces}');
INSERT INTO public.products VALUES (339, 'Potato P.P', '{bag,kg,pieces}');
INSERT INTO public.products VALUES (340, 'Potato Red', '{bag}');
INSERT INTO public.products VALUES (341, 'Potato Red Large', '{bag}');
INSERT INTO public.products VALUES (342, 'Potato Selected', '{bag}');
INSERT INTO public.products VALUES (343, 'Potato Simply', '{bag,kg}');
INSERT INTO public.products VALUES (344, 'Potato Sweet', '{bag,kg}');
INSERT INTO public.products VALUES (345, 'Potato TGS', '{bag}');
INSERT INTO public.products VALUES (346, 'Potato White', '{bag,kg}');
INSERT INTO public.products VALUES (347, 'Potato White Large', '{bag,kg}');
INSERT INTO public.products VALUES (348, 'Potol', '{bag,kg}');
INSERT INTO public.products VALUES (349, 'Pumpkin', '{box,kg,pieces}');
INSERT INTO public.products VALUES (350, 'pumpkin', '{bag}');
INSERT INTO public.products VALUES (351, 'Quince', '{box,kg,pieces}');
INSERT INTO public.products VALUES (352, 'Radish', '{box,pieces}');
INSERT INTO public.products VALUES (353, 'Radishio', '{box,pieces}');
INSERT INTO public.products VALUES (354, 'Rambutan', '{box,pieces}');
INSERT INTO public.products VALUES (355, 'Raspberry', '{box,pieces}');
INSERT INTO public.products VALUES (356, 'Raw Mango', '{box,kg,pieces}');
INSERT INTO public.products VALUES (357, 'Red Chard', '{box,kg,pieces}');
INSERT INTO public.products VALUES (358, 'Red Current', '{box,pieces}');
INSERT INTO public.products VALUES (359, 'Red Lolo', '{box,pieces}');
INSERT INTO public.products VALUES (360, 'Red Potato Jumbo', '{box}');
INSERT INTO public.products VALUES (361, 'Rice', '{bag,kg}');
INSERT INTO public.products VALUES (362, 'Rice guru', '{bag}');
INSERT INTO public.products VALUES (363, 'Rocket', '{kg}');
INSERT INTO public.products VALUES (364, 'Rocket Chilli', '{box,kg}');
INSERT INTO public.products VALUES (365, 'Rocket Chilli Large', '{box,kg}');
INSERT INTO public.products VALUES (366, 'Rocket Leaf', '{box,pieces}');
INSERT INTO public.products VALUES (367, 'Rokcet Leaf', '{box,kg,pieces}');
INSERT INTO public.products VALUES (368, 'Roman(rod)', '{box}');
INSERT INTO public.products VALUES (369, 'Romero Green', '{box,kg,pieces}');
INSERT INTO public.products VALUES (370, 'Romero Red', '{box,kg,pieces}');
INSERT INTO public.products VALUES (371, 'Rose Merry', '{box,bunch}');
INSERT INTO public.products VALUES (372, 'Rosmali', '{box}');
INSERT INTO public.products VALUES (373, 'Rosogalla', '{box}');
INSERT INTO public.products VALUES (374, 'Round Lettuce', '{box,pieces}');
INSERT INTO public.products VALUES (375, 'Round Shallot', '{box}');
INSERT INTO public.products VALUES (376, 'Runner Beans', '{box}');
INSERT INTO public.products VALUES (377, 'Safron', '{box,pieces}');
INSERT INTO public.products VALUES (378, 'Salad MIX', '{box}');
INSERT INTO public.products VALUES (379, 'Salgom', '{box,kg,pieces}');
INSERT INTO public.products VALUES (380, 'savoy cabbage', '{box,pieces}');
INSERT INTO public.products VALUES (381, 'Shakura', '{box,pieces}');
INSERT INTO public.products VALUES (382, 'Shallot Round', '{bag,pieces}');
INSERT INTO public.products VALUES (383, 'Sharon Fruit', '{box}');
INSERT INTO public.products VALUES (384, 'Shatkora', '{box,pieces}');
INSERT INTO public.products VALUES (385, 'Shitake Mushroom', '{box}');
INSERT INTO public.products VALUES (386, 'Shorifa', '{box}');
INSERT INTO public.products VALUES (387, 'Single Cream', '{box,pieces}');
INSERT INTO public.products VALUES (388, 'Sira', '{box,pieces}');
INSERT INTO public.products VALUES (389, 'Sisinda', '{box,kg}');
INSERT INTO public.products VALUES (390, 'Siveri', '{box,kg,pieces}');
INSERT INTO public.products VALUES (391, 'Sivri', '{box,kg}');
INSERT INTO public.products VALUES (392, 'Somosa', '{box,pieces}');
INSERT INTO public.products VALUES (393, 'Somosa pad', '{box,pieces}');
INSERT INTO public.products VALUES (394, 'Spinach', '{box,pieces}');
INSERT INTO public.products VALUES (395, 'Spinach baby', '{box,bunch}');
INSERT INTO public.products VALUES (396, 'Spinach frozen', '{box,bunch}');
INSERT INTO public.products VALUES (397, 'Spring Green', '{box,pieces}');
INSERT INTO public.products VALUES (398, 'Staff Veg', '{box,kg}');
INSERT INTO public.products VALUES (399, 'Strawberry', '{box,pieces}');
INSERT INTO public.products VALUES (400, 'Suger', '{box,kg}');
INSERT INTO public.products VALUES (401, 'Suger snap', '{box}');
INSERT INTO public.products VALUES (402, 'Supari', '{bag,kg}');
INSERT INTO public.products VALUES (403, 'Supari 10kg', '{bag}');
INSERT INTO public.products VALUES (404, 'Supari 5kg', '{bag}');
INSERT INTO public.products VALUES (405, 'Swede', '{bag,kg,pieces}');
INSERT INTO public.products VALUES (406, 'Sweet Corn', '{box,pieces}');
INSERT INTO public.products VALUES (407, 'Tangerines', '{box,kg,pieces}');
INSERT INTO public.products VALUES (408, 'Thai Basil', '{box,bunch}');
INSERT INTO public.products VALUES (409, 'Thai red chilli', '{box,kg}');
INSERT INTO public.products VALUES (410, 'Thime', '{box,pieces}');
INSERT INTO public.products VALUES (411, 'Thoikor', '{box,kg,pieces}');
INSERT INTO public.products VALUES (412, 'Thur', '{box,pieces}');
INSERT INTO public.products VALUES (413, 'Tikka Paste', '{box,pieces}');
INSERT INTO public.products VALUES (414, 'Tilda Basmati Rice', '{bag}');
INSERT INTO public.products VALUES (415, 'Tinda', '{box,kg}');
INSERT INTO public.products VALUES (416, 'Tomato', '{box}');
INSERT INTO public.products VALUES (417, 'Tomato beef', '{kg,pieces}');
INSERT INTO public.products VALUES (418, 'Tomato Beef', '{box}');
INSERT INTO public.products VALUES (419, 'Tomato cherry', '{pieces}');
INSERT INTO public.products VALUES (420, 'Tomato Cherry', '{box,kg}');
INSERT INTO public.products VALUES (421, 'Tomato peeled', '{box,pieces}');
INSERT INTO public.products VALUES (422, 'Tomato plum', '{box,kg}');
INSERT INTO public.products VALUES (423, 'Tomato puri', '{box,pieces}');
INSERT INTO public.products VALUES (424, 'Tomato Vine', '{box,kg}');
INSERT INTO public.products VALUES (425, 'Tufu', '{box}');
INSERT INTO public.products VALUES (426, 'Tufu Large', '{box}');
INSERT INTO public.products VALUES (427, 'Turkish chilli', '{box,pieces}');
INSERT INTO public.products VALUES (428, 'Turnip', '{box,kg}');
INSERT INTO public.products VALUES (429, 'Uri', '{box,kg}');
INSERT INTO public.products VALUES (430, 'Uri Lubi', '{box,kg}');
INSERT INTO public.products VALUES (431, 'Uri LUBI', '{box,kg}');
INSERT INTO public.products VALUES (432, 'Veg Roll', '{box,kg,pieces}');
INSERT INTO public.products VALUES (433, 'Veg Root', '{box,kg,pieces}');
INSERT INTO public.products VALUES (434, 'veg samosa', '{bag,pieces}');
INSERT INTO public.products VALUES (435, 'vegetable oil 20 Lt', '{box}');
INSERT INTO public.products VALUES (436, 'Water Melon', '{box,pieces}');
INSERT INTO public.products VALUES (437, 'Wiilliam pear', '{box,kg}');
INSERT INTO public.products VALUES (438, 'Wild Rocket Leaf', '{box,pieces}');
INSERT INTO public.products VALUES (439, 'William grapes', '{box,kg}');
INSERT INTO public.products VALUES (440, 'Yam', '{box,kg}');
INSERT INTO public.products VALUES (441, 'Yam (Cush)', '{box,kg,pieces}');
INSERT INTO public.products VALUES (442, 'Yam (Puna)', '{box,kg,pieces}');
INSERT INTO public.products VALUES (443, 'Yellow Colour', '{box,pieces}');
INSERT INTO public.products VALUES (444, 'Yellow Melon', '{box,pieces}');
INSERT INTO public.products VALUES (445, 'Yellow Plantain', '{box,kg,pieces}');
INSERT INTO public.products VALUES (446, 'Yogurt', '{bucket}');
INSERT INTO public.products VALUES (447, 'Yogurt ( greek yogurt )', '{box}');
INSERT INTO public.products VALUES (448, 'Yogurt 5kg', '{box}');
INSERT INTO public.products VALUES (449, 'Zinga', '{box}');
INSERT INTO public.products VALUES (236, 'Mint Leaf', '{pieces,box}');
INSERT INTO public.products VALUES (36, 'Avocado', '{box,pieces}');


--
-- TOC entry 4826 (class 0 OID 41203)
-- Dependencies: 220
-- Data for Name: restaurants; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.restaurants VALUES (1, 'Spice Merchant', '+441234567890');
INSERT INTO public.restaurants VALUES (2, 'My Test Restaurant', NULL);


--
-- TOC entry 4840 (class 0 OID 0)
-- Dependencies: 223
-- Name: client_phone_numbers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.client_phone_numbers_id_seq', 4, true);


--
-- TOC entry 4841 (class 0 OID 0)
-- Dependencies: 221
-- Name: clients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.clients_id_seq', 2, true);


--
-- TOC entry 4842 (class 0 OID 0)
-- Dependencies: 217
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_id_seq', 1, false);


--
-- TOC entry 4843 (class 0 OID 0)
-- Dependencies: 219
-- Name: restaurants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.restaurants_id_seq', 3, true);


--
-- TOC entry 4674 (class 2606 OID 41246)
-- Name: client_phone_numbers client_phone_numbers_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_phone_numbers
    ADD CONSTRAINT client_phone_numbers_phone_number_key UNIQUE (phone_number);


--
-- TOC entry 4676 (class 2606 OID 41244)
-- Name: client_phone_numbers client_phone_numbers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_phone_numbers
    ADD CONSTRAINT client_phone_numbers_pkey PRIMARY KEY (id);


--
-- TOC entry 4672 (class 2606 OID 41234)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- TOC entry 4662 (class 2606 OID 41199)
-- Name: products products_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_name_key UNIQUE (name);


--
-- TOC entry 4664 (class 2606 OID 41197)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 4666 (class 2606 OID 41212)
-- Name: restaurants restaurants_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_name_key UNIQUE (name);


--
-- TOC entry 4668 (class 2606 OID 41214)
-- Name: restaurants restaurants_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_phone_number_key UNIQUE (phone_number);


--
-- TOC entry 4670 (class 2606 OID 41210)
-- Name: restaurants restaurants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_pkey PRIMARY KEY (id);


--
-- TOC entry 4677 (class 2606 OID 41247)
-- Name: client_phone_numbers client_phone_numbers_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_phone_numbers
    ADD CONSTRAINT client_phone_numbers_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


-- Completed on 2025-11-12 11:08:07

--
-- PostgreSQL database dump complete
--

