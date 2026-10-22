<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress');

/** MySQL database username */
define( 'DB_USER', 'wpuser');

/** MySQL database password */
define( 'DB_PASSWORD', 'wp123');

/** MySQL hostname */
define( 'DB_HOST', 'mysql:3306');

/** Database Charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'c1b76b3964a8b148a46dffc4a2e017a6821674df');
define( 'SECURE_AUTH_KEY',  'bacd879878ab2d14b2e52863d40810ce244de7b4');
define( 'LOGGED_IN_KEY',    '1de4d92b7c4377b6e74814e9cb3c1de28e38479b');
define( 'NONCE_KEY',        'e8e854915405dc1d3d4c396be1a410c7429d21c4');
define( 'AUTH_SALT',        '160c8eb68f946f2835f350022e0681eded21fd34');
define( 'SECURE_AUTH_SALT', '960a7a88694633b65e8a60b42082c2745d318375');
define( 'LOGGED_IN_SALT',   '310d0547db258f89c611838c063abf2acf3e9f39');
define( 'NONCE_SALT',       '90bc67449812b3e3c1d4cc55f8b37559f9c60270');

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

// If we're behind a proxy server and using HTTPS, we need to alert WordPress of that fact
// see also http://codex.wordpress.org/Administration_Over_SSL#Using_a_Reverse_Proxy
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
	$_SERVER['HTTPS'] = 'on';
}

// Site URL dinamica baseada no cabecalho Host da requisicao. Isso permite
// acessar o mesmo WordPress tanto via http://localhost:8081 (navegador, via
// mapeamento de porta do Nginx) quanto via http://nginx (rede interna do
// Docker, usada pelo Locust no Trabalho 3) sem gerar redirecionamentos para
// uma URL fixa que nao seria alcancavel a partir do outro contexto.
if (isset($_SERVER['HTTP_HOST'])) {
	define('WP_HOME', 'http://' . $_SERVER['HTTP_HOST']);
	define('WP_SITEURL', 'http://' . $_SERVER['HTTP_HOST']);
}

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
