/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line_utils.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/09 16:56:51 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/12 18:26:41 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line.h"

void	*ft_memcpy(void *dest, const void *src, size_t num)
{
	size_t	idx;

	idx = 0;
	while (idx < num)
	{
		((unsigned char *)dest)[idx] = ((unsigned char *)src)[idx];
		idx++;
	}
	return (dest);
}

size_t	ft_strlen(const char *s)
{
	size_t	i;

	if (!s)
		return (0);
	i = 0;
	while (s[i])
		i++;
	return (i);
}

char	*append(char *dest, char *src, size_t n)
{
	size_t	dest_len;
	char	*new;

	dest_len = ft_strlen(dest);
	new = malloc(dest_len + n + 1);
	if (!new)
	{
		free(dest);
		return (NULL);
	}
	ft_memcpy(new, dest, dest_len);
	ft_memcpy(new + dest_len, src, n);
	new[dest_len + n] = '\0';
	free(dest);
	return (new);
}

int	find_nl(const char *s)
{
	int	i;

	if (!s)
		return (-1);
	i = 0;
	while (s[i])
	{
		if (s[i] == '\n')
			return (i);
		i++;
	}
	return (-1);
}
