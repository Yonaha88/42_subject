/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/09 11:23:56 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/12 18:26:41 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line.h"

static char	*read_to_remainder(int fd, char *rem)
{
	char	*buf;
	int		ret;
	size_t	scan_from;

	if (find_nl(rem) >= 0)
		return (rem);
	buf = malloc(BUFFER_SIZE + 1);
	if (!buf)
		return (rem);
	scan_from = ft_strlen(rem);
	while (1)
	{
		ret = read(fd, buf, BUFFER_SIZE);
		if (ret <= 0)
			break ;
		rem = append(rem, buf, (size_t)ret);
		if (!rem)
			break ;
		if (find_nl(rem + scan_from) >= 0)
			break ;
		scan_from += (size_t)ret;
	}
	free(buf);
	return (rem);
}

static char	*update_remainder(char *rem, int nl)
{
	char	*new_rem;
	size_t	len;

	if (nl < 0 || !rem[nl + 1])
		return (NULL);
	len = ft_strlen(rem + nl + 1);
	new_rem = malloc(len + 1);
	if (!new_rem)
		return (NULL);
	ft_memcpy(new_rem, rem + nl + 1, len + 1);
	return (new_rem);
}

static char	*extract_line(char **rem)
{
	int		nl;
	size_t	line_len;
	char	*line;
	char	*new_rem;

	if (!*rem || !**rem)
	{
		free(*rem);
		*rem = NULL;
		return (NULL);
	}
	nl = find_nl(*rem);
	if (nl >= 0)
		line_len = (size_t)(nl + 1);
	else
		line_len = ft_strlen(*rem);
	line = malloc(line_len + 1);
	if (!line)
		return (NULL);
	ft_memcpy(line, *rem, line_len);
	line[line_len] = '\0';
	new_rem = update_remainder(*rem, nl);
	free(*rem);
	*rem = new_rem;
	return (line);
}

char	*get_next_line(int fd)
{
	static char	*remainder[OPEN_MAX];

	if (fd < 0 || fd >= OPEN_MAX || BUFFER_SIZE <= 0)
		return (NULL);
	remainder[fd] = read_to_remainder(fd, remainder[fd]);
	return (extract_line(&remainder[fd]));
}
