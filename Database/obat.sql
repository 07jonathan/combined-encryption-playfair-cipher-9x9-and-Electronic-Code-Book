-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 04 Feb 2024 pada 11.22
-- Versi server: 10.4.27-MariaDB
-- Versi PHP: 8.1.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `enkripsi`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `obat`
--

CREATE TABLE `obat` (
  `id_obat` int(11) NOT NULL,
  `nama_obat` varchar(255) DEFAULT NULL,
  `kategori` varchar(255) DEFAULT NULL,
  `bentuk` varchar(255) DEFAULT NULL,
  `dosis` varchar(255) DEFAULT NULL,
  `cara_penggunaan` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `obat`
--

INSERT INTO `obat` (`id_obat`, `nama_obat`, `kategori`, `bentuk`, `dosis`, `cara_penggunaan`) VALUES
(1, 'X&', '6L4', '6L4', '6L4', '6L4'),
(2, '\n2hÌ', '\0*8ªN', '<L', 'þ8', '<.¤|\n¾¤¢ò4¾x\n'),
(3, '>(8¬ ', '(B2¨', '<L', '\Z8', '<.\n\Z\nHh²&ª´ä2<.2¼\n'),
(4, '\n6:°¾', '.¼Ô¦üX&<', 'þL>.ºª', 'Pª°66¦', '<.r\n\n¤¾86²¼°¤®&2,(fºÎ'),
(5, '>ºÂ\n¬N', '\08¢®¸<', 'þL>.ºª', 'P°66¦', '<.r\n\n¤¾86² ºâ°Äþn(z\nÂx@,(fºÎÂ'),
(6, '&:ª¬î|$n(\n', '$0J\"ºªÎ', '<L', 'P,(\n', '<.r\n\"¾ØþD\n$¼Ò¦ø|²vnhºÀ°Þþ@´2'),
(7, '<.:*<Ìªì', '\08¢®¸<', '<L', '\Z,(\n', '<.r\n\n¤¾86² ºâ°Äþn(z\nÂx@,(fºÎÂ'),
(8, '\n4$¨N', '\08¢0¨ð$', '<L', 'þ8', '<.r\n\n¤¾86²¼°¤®&2,(fºÎ'),
(9, '\nbv2Â', '\0*8ªN', '<L', 'P,(\n', '<.¤|\n¾¤¢ò4¾x\n'),
(10, '¤<Ð¬0', '\08¢®¸<', '<L', '\0`,(\n', '<.r\n\n¤¾86² ºâ°Äþn(z\nÂx@,(fºÎÂ'),
(11, '4\n<Ì ,', '$0J\"ºªÎ', '<L', '\0`,(\n', '<.r\n\"¾ØþD\n$¼Ò¦ø|²vnhºÀ°Þþ@´2'),
(12, '2X:&&¦ì', '\08¢®¸<', '<L', 'P,(\n', '<.r\n\n¤¾86² ºâ°Äþn(z\nÂx@,(fºÎÂ'),
(13, '2@&>ì\n¬N', '.\" Ô¦üX&<', '<L', '\Z,(\n', '8\nÖªZ>r(8¾îND´2`Ì<2l\"Ð¾Â<'),
(14, ',2t\ZÎ', '\08¢®¸<', '<L', 'P,(\n', '<.r\n\n¤¾86² ºâ°Äþn(z\nÂx@,(fºÎÂ'),
(15, '8b6$6à.¨v2®¢d(\n<Ìºxv', '<\"2h6¾îR°h¶È\0P*6', '2>&2¶\n', 'ð,(\n', '<.r\n\n¤¾86²&Ì¾°,x@8N¼ºÊ\0'),
(16, '\nv2 ', '\":|ø t\0\n<', '<L', 'þ8', '<.r\n\n¤¾86²¼¨®¤®\04¬(8¬¶¸'),
(17, '>^4&¦ì', '\08¢®¸<', 'þL>.ºª', 'Pª,(\n', '<.r\n\n¤¾86²&Ê¾\0$t®\"¼Î');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `obat`
--
ALTER TABLE `obat`
  ADD PRIMARY KEY (`id_obat`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `obat`
--
ALTER TABLE `obat`
  MODIFY `id_obat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
