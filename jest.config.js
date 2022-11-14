module.exports = {
  roots: ['<rootDir>'],
  moduleFileExtensions: ['js', 'ts', 'tsx', 'json'],
  moduleNameMapper: {
    '^/static(.*)$': '<rootDir>/cen/static$1',
  },
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  "setupFiles": [
      "./setupJest.js"
],
};