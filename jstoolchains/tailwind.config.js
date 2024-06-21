/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		'../templates/**/*.html',
		'../accounts/templates/**/*.html',
		'../chat/templates/**/*.html',
	],
	theme: {
		extend: {},
	},
	plugins: [require('daisyui')],
	daisyui: {
		themes: ['light', 'dark'],
	},
};
