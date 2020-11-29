module.exports = {
    future: {
        removeDeprecatedGapUtilities: true,
        purgeLayersByDefault: true,
    },
    purge: { enabled: true, content: ["./**/*.html"] },
    theme: {
        fontFamily: {
            body: ["Source Sans Pro", "sans-serif"],
            mono: ["SFMono-Regular", "Menlo", "monospace"],
        },
        extend: {
            colors: {
                iblue: {
                    default: "#1a7cbd",
                    light: "#45b4ff",
                    dark: "#184766",
                },
                iyellow: {
                    default: "#fffade",
                    dark: "#887131",
                },
            },
        },
    },
    variants: {},
    plugins: [],
};
