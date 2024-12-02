FROM node:20-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

RUN pnpm install

COPY . .

# Accept build-time arguments for environment variables
ARG NEXT_PUBLIC_AUTH_API
ARG NEXT_PUBLIC_LOG_API

# Set environment variables in the container
ENV NEXT_PUBLIC_AUTH_API=$NEXT_PUBLIC_AUTH_API
ENV NEXT_PUBLIC_LOG_API=$NEXT_PUBLIC_LOG_API

EXPOSE 3000

RUN pnpm build

CMD ["pnpm", "start"]

